"""
MQTT Consumer для приема данных Wi-Fi мониторинга
- Поддерживает форматы:
  1) [{"m":"aa:bb:..","r":-63,"t":1700000000,"x":0}, ...]
  2) {"t":1700000000,"d":[{"m":"aa:bb:..","r":-63,"x":0}, ...], "c":123}
- Всегда обновляет статистику хранилища (даже если устройств 0 после фильтра)
- Более устойчивое переподключение к брокеру
"""
import json
import logging
import signal
import sys
import time
from typing import Any, Dict, List, Optional

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC,
    MQTT_CLIENT_ID,
    ENABLE_DEVICE_FILTERING,
    ALLOWED_DEVICE_TYPES,
)
from storage import WiFiDataStorage
from device_classifier import classify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mqtt_consumer")


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


class MQTTConsumer:
    """MQTT Consumer для приема и обработки данных"""

    def __init__(self, storage: WiFiDataStorage):
        self.storage = storage
        self.running = False

        # Поддержка paho-mqtt v1 и v2 (убирает DeprecationWarning на новых версиях)
        self.client = self._create_client()

        # callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # более мягкая стратегия реконнекта (внутренняя)
        try:
            self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        except Exception:
            pass

    def _create_client(self) -> mqtt.Client:
        """
        Создает MQTT client совместимо с paho-mqtt:
        - v2: mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, ...)
        - v1: mqtt.Client(client_id=...)
        """
        # MQTT v3.1.1 самый совместимый
        protocol = getattr(mqtt, "MQTTv311", mqtt.MQTTv31)

        if hasattr(mqtt, "CallbackAPIVersion"):
            # paho-mqtt 2.x
            return mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=MQTT_CLIENT_ID,
                protocol=protocol,
            )

        # paho-mqtt 1.x
        return mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=protocol)

    # --- MQTT callbacks (делаем сигнатуры гибкими через *args) ---

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: Any, *args: Any, **kwargs: Any) -> None:
        """
        v1: rc=int
        v2: rc=ReasonCode (имеет .value)
        """
        code = rc.value if hasattr(rc, "value") else rc
        code = _safe_int(code, 255)

        if code == 0:
            logger.info(f"Подключено к MQTT брокеру {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            try:
                client.subscribe(MQTT_TOPIC, qos=0)
            except TypeError:
                client.subscribe(MQTT_TOPIC)
            logger.info(f"Подписка на топик: {MQTT_TOPIC}")
        else:
            logger.error(f"Ошибка подключения к MQTT брокеру. Код: {code}")

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: Any, *args: Any, **kwargs: Any) -> None:
        code = rc.value if hasattr(rc, "value") else rc
        code = _safe_int(code, 0)

        if not self.running:
            logger.info("Отключено от MQTT брокера (остановка consumer)")
            return

        # rc != 0 — нештатное отключение
        if code != 0:
            logger.warning(f"Неожиданное отключение от MQTT брокера. Код: {code}. Пытаюсь переподключиться...")
            # loop_start() уже крутится, поэтому просто пробуем reconnect в фоне
            for attempt in range(1, 11):
                if not self.running:
                    return
                try:
                    time.sleep(min(2 * attempt, 10))
                    client.reconnect()
                    logger.info("Переподключение успешно")
                    return
                except Exception as e:
                    logger.warning(f"reconnect попытка {attempt}/10 не удалась: {e}")
            logger.error("Не удалось переподключиться к MQTT брокеру после 10 попыток")
        else:
            logger.info("Отключено от MQTT брокера")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        payload_raw = ""
        try:
            payload_raw = msg.payload.decode("utf-8", errors="replace").strip()
            if not payload_raw:
                # Пустое сообщение — всё равно обновим статистику
                self.storage.add_data([])
                logger.warning("Получено пустое MQTT сообщение (payload пустой)")
                return

            data = json.loads(payload_raw)
            devices_data = self._parse_data(data)

            # ВСЕГДА обогащаем данные классификацией (до фильтрации)
            enriched_data = self._enrich_devices(devices_data)

            # Фильтрация (если включена) - применяется после enrichment
            if ENABLE_DEVICE_FILTERING:
                filtered = self._filter_devices(enriched_data)
                # ВАЖНО: обновляем статистику ВСЕГДА
                self.storage.add_data(filtered)
                logger.info(f"Устройства: получено {len(devices_data)}, обогащено {len(enriched_data)}, после фильтра {len(filtered)}")
            else:
                self.storage.add_data(enriched_data)
                logger.info(f"Устройства: получено {len(devices_data)}, обогащено {len(enriched_data)}")

        except json.JSONDecodeError as e:
            # Если в MQTT прилетает НЕ-JSON (например {m:aa...} без кавычек) — это будет сюда
            logger.error(f"Ошибка парсинга JSON: {e}. Первые 120 символов: {payload_raw[:120]!r}")
            # Всё равно двигаем статистику, чтобы API не “стоял”
            self.storage.add_data([])
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
            # Всё равно двигаем статистику
            self.storage.add_data([])

    # --- parsing / filtering ---

    def _parse_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Возвращает список элементов вида:
        {"m": "...", "r": -63, "t": 170..., "x": 0}
        """
        out: List[Dict[str, Any]] = []

        # Формат A: list[dict]
        if isinstance(data, list):
            for item in data:
                parsed = self._parse_item(item, root_timestamp=None)
                if parsed is not None:
                    out.append(parsed)
            return out

        # Формат B: {"t":..., "d":[...], ...}
        if isinstance(data, dict):
            root_ts = data.get("t", 0)
            devices = data.get("d", [])
            if isinstance(devices, list):
                for item in devices:
                    parsed = self._parse_item(item, root_timestamp=root_ts)
                    if parsed is not None:
                        out.append(parsed)
            return out

        return out

    def _parse_item(self, item: Any, root_timestamp: Optional[Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(item, dict):
            return None

        mac = item.get("m")
        if not isinstance(mac, str) or not mac:
            return None

        # rssi может быть в "r" или "s"
        rssi = item.get("r", item.get("s", 0))
        rssi = _safe_int(rssi, 0)

        # timestamp может быть в item["t"], иначе root_timestamp, иначе 0
        ts = item.get("t", root_timestamp if root_timestamp is not None else 0)
        ts = _safe_int(ts, 0)
        if ts <= 0:
            ts = int(time.time())

        # флаг randomized может быть item["x"]; (иногда его путают с "r" — но r у нас уже RSSI)
        x = item.get("x", None)
        if x is not None:
            x = _safe_int(x, 0)

        return {"m": mac, "r": rssi, "t": ts, "x": x}

    def _enrich_devices(self, devices_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Обогащение данных классификацией устройств.
        Вызывается ВСЕГДА после парсинга и ДО фильтрации.
        
        Args:
            devices_data: Список устройств с полями m, r, t, x
            
        Returns:
            Список устройств с добавленными полями vendor, device_type, device_brand, randomized
        """
        enriched: List[Dict[str, Any]] = []
        
        for d in devices_data:
            mac = d.get("m", "")
            rssi = d.get("r", 0)
            x = d.get("x", None)
            
            # Классификация устройства
            cls = classify(mac, rssi, x)
            
            # Добавляем поля классификации к существующим данным
            d.update({
                "vendor": cls.get("vendor"),
                "device_type": cls.get("device_type", "other"),
                "device_brand": cls.get("device_brand"),
                "randomized": cls.get("randomized", False),
            })
            enriched.append(d)
        
        return enriched

    def _filter_devices(self, devices_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрация устройств по типу.
        Вызывается ПОСЛЕ enrichment, использует уже обогащенные данные.
        
        Args:
            devices_data: Список обогащенных устройств (с полями device_type)
            
        Returns:
            Отфильтрованный список устройств (только разрешенные типы)
        """
        filtered: List[Dict[str, Any]] = []

        for d in devices_data:
            device_type = d.get("device_type", "other")
            
            # Фильтруем только по типу устройства (данные уже обогащены)
            if device_type in ALLOWED_DEVICE_TYPES:
                filtered.append(d)

        return filtered

    # --- public API ---

    def start(self) -> None:
        logger.info(f"Подключение к MQTT брокеру {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        self.running = True

        # connect + loop
        self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        self.client.loop_start()
        logger.info("MQTT Consumer запущен")

    def stop(self) -> None:
        logger.info("Остановка MQTT Consumer...")
        self.running = False
        try:
            self.client.loop_stop()
        except Exception:
            pass
        try:
            self.client.disconnect()
        except Exception:
            pass
        logger.info("MQTT Consumer остановлен")


def main() -> None:
    storage = WiFiDataStorage()
    consumer = MQTTConsumer(storage)

    def _signal_handler(sig: int, frame: Any) -> None:
        logger.info("Получен сигнал завершения")
        consumer.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        consumer.start()
        while consumer.running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Прервано пользователем")
    finally:
        consumer.stop()


if __name__ == "__main__":
    main()
