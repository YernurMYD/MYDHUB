"""
Flask API для дашборда Wi-Fi мониторинга
"""
import logging
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import API_HOST, API_PORT
from storage import WiFiDataStorage

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для дашборда

# Логи (минимально, без спама)
logger = logging.getLogger("dashboard_api")

# Глобальное хранилище (будет установлено извне)
storage: WiFiDataStorage = None


def init_api(data_storage: WiFiDataStorage):
    """
    Инициализация API с хранилищем данных
    
    Args:
        data_storage: Экземпляр хранилища данных
    """
    global storage
    storage = data_storage


@app.route('/api/health', methods=['GET'])
def health():
    """Проверка работоспособности API"""
    return jsonify({"status": "ok"})


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Получение статистики"""
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    
    stats = storage.get_statistics()
    return jsonify(stats)


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """
    Получение списка устройств
    
    Query параметры:
        limit: Максимальное количество устройств (по умолчанию: все)
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    
    limit = request.args.get('limit', type=int)
    
    devices = storage.get_devices(limit=limit)
    
    # Формируем ответ с совместимостью со старым форматом
    # Старые поля (m, r) для совместимости с фронтендом
    devices_response = []
    for device in devices:
        device_dict = {
            "m": device.get("mac", ""),  # Старое поле для совместимости
            "mac": device.get("mac", ""),  # Новое поле
            "r": device.get("latest_rssi", device.get("best_rssi", 0)),  # Старое поле
            "rssi": device.get("latest_rssi", device.get("best_rssi", 0)),  # Новое поле
            "first_seen": device.get("first_seen", 0),
            "last_seen": device.get("last_seen", 0),
            "count": device.get("count", 0),
            "best_rssi": device.get("best_rssi", 0),
            "latest_rssi": device.get("latest_rssi", 0)
        }
        # Добавляем новые поля классификации
        if "vendor" in device:
            device_dict["vendor"] = device["vendor"]
        if "device_type" in device:
            device_dict["device_type"] = device["device_type"]
        if "device_brand" in device:
            device_dict["device_brand"] = device["device_brand"]
        if "randomized" in device:
            device_dict["randomized"] = device["randomized"]
        devices_response.append(device_dict)
    
    return jsonify({
        "devices": devices_response,
        "count": len(devices_response)
    })


@app.route('/api/devices/<mac>', methods=['GET'])
def get_device(mac: str):
    """Получение информации об устройстве по MAC адресу"""
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    
    devices = storage.get_devices()
    device = next((d for d in devices if d["mac"] == mac.lower()), None)
    
    if device:
        # Формируем ответ с совместимостью
        device_dict = {
            "m": device.get("mac", ""),  # Старое поле
            "mac": device.get("mac", ""),  # Новое поле
            "r": device.get("latest_rssi", device.get("best_rssi", 0)),  # Старое поле
            "rssi": device.get("latest_rssi", device.get("best_rssi", 0)),  # Новое поле
            "first_seen": device.get("first_seen", 0),
            "last_seen": device.get("last_seen", 0),
            "count": device.get("count", 0),
            "best_rssi": device.get("best_rssi", 0),
            "latest_rssi": device.get("latest_rssi", 0)
        }
        # Добавляем новые поля
        if "vendor" in device:
            device_dict["vendor"] = device["vendor"]
        if "device_type" in device:
            device_dict["device_type"] = device["device_type"]
        if "device_brand" in device:
            device_dict["device_brand"] = device["device_brand"]
        if "randomized" in device:
            device_dict["randomized"] = device["randomized"]
        return jsonify(device_dict)
    else:
        return jsonify({"error": "Device not found"}), 404


@app.route('/api/recent', methods=['GET'])
def get_recent():
    """
    Получение последних данных
    
    Query параметры:
        limit: Максимальное количество записей (по умолчанию: 100)
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    
    from flask import request
    limit = request.args.get('limit', default=100, type=int)
    
    recent = storage.get_recent_data(limit=limit)
    return jsonify({
        "data": recent,
        "count": len(recent)
    })


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Получение данных для дашборда
    
    Возвращает агрегированные данные для отображения
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    
    from flask import request
    limit = request.args.get('limit', default=100, type=int)
    
    # Получаем данные
    stats = storage.get_statistics()
    devices = storage.get_devices(limit=limit)
    recent = storage.get_recent_data(limit=50)
    
    # Формируем устройства с совместимостью
    top_devices_response = []
    for device in devices[:20]:
        device_dict = {
            "m": device.get("mac", ""),  # Старое поле
            "mac": device.get("mac", ""),  # Новое поле
            "r": device.get("latest_rssi", device.get("best_rssi", 0)),  # Старое поле
            "rssi": device.get("latest_rssi", device.get("best_rssi", 0)),  # Новое поле
            "first_seen": device.get("first_seen", 0),
            "last_seen": device.get("last_seen", 0),
            "count": device.get("count", 0),
            "best_rssi": device.get("best_rssi", 0),
            "latest_rssi": device.get("latest_rssi", 0)
        }
        # Добавляем новые поля
        if "vendor" in device:
            device_dict["vendor"] = device["vendor"]
        if "device_type" in device:
            device_dict["device_type"] = device["device_type"]
        if "device_brand" in device:
            device_dict["device_brand"] = device["device_brand"]
        if "randomized" in device:
            device_dict["randomized"] = device["randomized"]
        top_devices_response.append(device_dict)
    
    # Агрегация для дашборда
    dashboard_data = {
        "statistics": stats,
        "top_devices": top_devices_response,  # Топ 20 устройств
        "recent_activity": recent[-20:],  # Последние 20 записей
        "unique_devices_count": len(devices),
        "active_devices": len([d for d in devices if d["count"] > 1])
    }
    
    return jsonify(dashboard_data)


@app.route('/api/stats/realtime', methods=['GET'])
def get_realtime_stats():
    """
    Получение данных реального времени (последние 60 секунд)
    
    Формат ответа соответствует ожиданиям фронтенда:
    {
        "unique_devices": 42,
        "devices": [
            {
                "mac": "aa:bb:cc:dd:ee:ff",
                "rssi": -65,
                "timestamp": "2024-01-01T12:00:00Z",
                "is_random": false
            }
        ]
    }
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500

    # Берём последние точки и фильтруем окно 60 секунд (по unix ts источника).
    # ВАЖНО: используем storage.get_recent_data() как источник истины (по задаче).
    import time
    now_ts = int(time.time())
    cutoff_ts = now_ts - 60

    recent = storage.get_recent_data(limit=500)
    window = [e for e in recent if int(e.get("t", 0) or 0) >= cutoff_ts]

    # Кешируем информацию об устройствах (чтобы не делать storage.get_devices() в цикле)
    devices_index = {d.get("mac", "").lower(): d for d in storage.get_devices()}

    unique_macs = set()
    devices_list = []

    for ts_entry in window:
        ts = int(ts_entry.get("t", 0) or 0)
        devices = ts_entry.get("d", []) or []

        # ISO 8601 (UTC) для этой временной метки
        try:
            timestamp_iso = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, OSError, OverflowError):
            timestamp_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        for device in devices:
            mac = (device.get("m") or "").lower()
            if not mac or mac in unique_macs:
                continue

            unique_macs.add(mac)
            info = devices_index.get(mac, {})

            devices_list.append(
                {
                    "mac": mac,
                    "rssi": int(device.get("r", info.get("latest_rssi", info.get("best_rssi", 0))) or 0),
                    "timestamp": timestamp_iso,
                    "is_random": bool(info.get("randomized", False)),
                }
            )

    return jsonify({"unique_devices": len(unique_macs), "devices": devices_list})


def _parse_timeframe(tf: str):
    """Парсит timeframe 1h|12h|1d|30d -> (seconds, bucket_sec, label).
    Размер бакета подобран так, чтобы на графике было 6-24 точек."""
    tf = (tf or "1h").strip().lower()
    if tf == "1h":
        return 3600, 600, "1h"       # 6 точек по 10 мин
    if tf == "6h":
        return 21600, 900, "6h"      # 24 точки по 15 мин
    if tf == "12h":
        return 43200, 1800, "12h"    # 24 точки по 30 мин
    if tf == "1d":
        return 86400, 3600, "1d"     # 24 точки по 1 часу
    if tf == "30d":
        return 2592000, 86400, "30d" # 30 точек по 1 дню
    return 3600, 600, "1h"


@app.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    """
    Сводка метрик для верхних карточек дашборда:
    - peak_all_time: максимум уникальных устройств за всё время (в одном снимке)
    - last_snapshot: кол-во уникальных устройств в последнем снимке роутера
    - total_unique: общее кол-во уникальных MAC за всё время работы
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500

    summary = storage.get_snapshot_summary()
    return jsonify(summary)


@app.route('/api/stats/count', methods=['GET'])
def get_device_count():
    """
    Уникальные устройства за период (last_seen в [start_ts, end_ts]).
    timeframe: 1h|6h|12h|1d|30d
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500

    tf_str = (request.args.get("timeframe", "1h") or "1h").strip().lower()
    timeframe_sec, _, _ = _parse_timeframe(tf_str)

    now_ts = int(time.time())
    devices = storage.get_devices()
    recent = storage.get_recent_data(limit=500)

    end_ts = now_ts
    for d in devices:
        ls = int(d.get("last_seen", 0) or 0)
        if ls > 0 and ls > end_ts:
            end_ts = ls
    for e in recent:
        t = int(e.get("t", 0) or 0)
        if t > 0 and t > end_ts:
            end_ts = t

    start_ts = end_ts - timeframe_sec
    count = 0
    for d in devices:
        ls = int(d.get("last_seen", 0) or 0)
        if ls <= 0:
            continue
        if start_ts <= ls <= end_ts:
            count += 1

    return jsonify({"timeframe": tf_str, "count": count, "start_ts": start_ts, "end_ts": end_ts})


@app.route('/api/stats/timeseries', methods=['GET'])
def get_devices_timeseries():
    """
    Устаревший alias: редирект на devices_timeseries с числовым timeframe.
    """
    tf = request.args.get("timeframe", "1h")
    if isinstance(tf, str) and tf.isdigit():
        mapping = {"60": "1h", "360": "6h", "720": "12h"}
        tf = mapping.get(tf, "1h")
    return _devices_timeseries_impl(tf)


@app.route('/api/stats/devices_timeseries', methods=['GET'])
def get_devices_timeseries_new():
    """
    Временной ряд: количество уникальных устройств по бакетам времени.
    GET /api/stats/devices_timeseries?timeframe=1h|6h|12h|1d|30d
    Ответ: { timeframe, start_ts, end_ts, bucket_sec, points: [{t, count}, ...] }
    """
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    tf_str = (request.args.get("timeframe", "1h") or "1h").strip().lower()
    return _devices_timeseries_impl(tf_str)


def _devices_timeseries_impl(timeframe_str: str):
    timeframe_sec, bucket_sec, label = _parse_timeframe(timeframe_str)

    now_ts = int(time.time())
    end_ts = now_ts
    start_ts = end_ts - timeframe_sec

    start_bucket = (start_ts // bucket_sec) * bucket_sec
    end_bucket = (end_ts // bucket_sec) * bucket_sec

    # ── Строим бакеты ──
    bucket_starts = []
    t = start_bucket
    while t <= end_bucket:
        bucket_starts.append(t)
        t += bucket_sec

    # Берём ВСЕ устройства (devices dict — уникальны по MAC, без дупликатов)
    devices = storage.get_devices()

    # Для каждого бакета считаем устройства, которые были «активны» в этом интервале.
    # Устройство считается активным в бакете [b, b+bucket_sec), если:
    #   first_seen < b + bucket_sec  И  last_seen >= b
    # Т.е. оно появилось до конца бакета и ещё не исчезло к его началу.
    points = []
    last_known = 0
    for b in bucket_starts:
        bucket_end = b + bucket_sec
        count = 0
        for d in devices:
            fs = int(d.get("first_seen", 0) or 0)
            ls = int(d.get("last_seen", 0) or 0)
            if ls <= 0:
                continue
            if fs < bucket_end and ls >= b:
                count += 1

        if count > 0:
            last_known = count
        else:
            # Forward-fill: пока нет новых данных, держим последнее
            # известное значение (роутер шлёт раз в 10 мин, между
            # отправками устройства никуда не исчезают)
            count = last_known

        points.append({"t": b, "count": count})

    logger.info("devices_timeseries timeframe=%s bucket_sec=%s points=%s", label, bucket_sec, len(points))
    return jsonify({
        "timeframe": label,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "bucket_sec": bucket_sec,
        "points": points,
    })


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Очистка всех данных (только для разработки)"""
    if not storage:
        return jsonify({"error": "Storage not initialized"}), 500
    
    storage.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    # Для тестирования без consumer
    from storage import WiFiDataStorage
    test_storage = WiFiDataStorage()
    init_api(test_storage)
    app.run(host=API_HOST, port=API_PORT, debug=True)
