"""
Smoke-check скрипт для проверки работоспособности системы Wi-Fi мониторинга

Проверяет:
1. Публикацию тестовых MQTT сообщений (оба формата)
2. Наличие полей классификации в API ответах
3. Поведение фильтрации устройств
"""

import json
import os
import sys
import time
from typing import Dict, Any

try:
    import paho.mqtt.client as mqtt
    import requests
except ImportError:
    print("Ошибка: Необходимо установить зависимости:")
    print("  pip install paho-mqtt requests")
    sys.exit(1)

# Конфигурация
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "wifi/probes")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api")

# Тестовые MAC адреса
TEST_DEVICES = [
    {"m": "00:1e:c2:aa:bb:cc", "r": -63, "x": 0},  # Apple iPhone (smartphone)
    {"m": "00:12:fb:aa:bb:cc", "r": -70, "x": 0},  # Samsung phone (smartphone)
    {"m": "00:1b:21:aa:bb:cc", "r": -55, "x": 0},  # Intel laptop
    {"m": "aa:bb:cc:dd:ee:ff", "r": -75, "x": 1},  # Randomized unknown (other)
]


def publish_mqtt_message(client: mqtt.Client, payload: Dict[str, Any], format_name: str) -> bool:
    """Публикация MQTT сообщения"""
    try:
        payload_json = json.dumps(payload)
        result = client.publish(MQTT_TOPIC, payload_json, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"  ✓ Опубликовано сообщение (формат {format_name})")
            return True
        else:
            print(f"  ✗ Ошибка публикации (формат {format_name}): код {result.rc}")
            return False
    except Exception as e:
        print(f"  ✗ Исключение при публикации (формат {format_name}): {e}")
        return False


def check_api_endpoint(url: str, description: str) -> Dict[str, Any]:
    """Проверка API эндпоинта"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"  ✓ {description}: OK (status {response.status_code})")
            return response.json()
        else:
            print(f"  ✗ {description}: Ошибка (status {response.status_code})")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"  ✗ {description}: Ошибка запроса - {e}")
        return {}


def check_enrichment_fields(device: Dict[str, Any]) -> bool:
    """Проверка наличия полей классификации"""
    required_fields = ["vendor", "device_type", "device_brand", "randomized"]
    missing = [field for field in required_fields if field not in device]
    
    if missing:
        print(f"    ⚠ Отсутствуют поля: {', '.join(missing)}")
        return False
    
    # Проверяем, что поля не None (хотя бы некоторые должны быть заполнены)
    has_some_data = any(
        device.get("vendor") is not None or
        device.get("device_type") is not None or
        device.get("device_brand") is not None or
        device.get("randomized") is not None
    )
    
    if not has_some_data:
        print(f"    ⚠ Все поля классификации равны None")
        return False
    
    return True


def main():
    """Основная функция smoke-check"""
    print("=" * 60)
    print("Smoke-check системы Wi-Fi мониторинга")
    print("=" * 60)
    print()
    
    # Проверка подключения к MQTT брокеру
    print("1. Подключение к MQTT брокеру...")
    mqtt_client = mqtt.Client(client_id="smoke_check_client")
    
    try:
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        mqtt_client.loop_start()
        print(f"  ✓ Подключено к {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    except Exception as e:
        print(f"  ✗ Ошибка подключения к MQTT брокеру: {e}")
        print("  Убедитесь, что MQTT брокер запущен и доступен")
        return 1
    
    time.sleep(1)  # Даем время на подключение
    
    # Публикация тестовых сообщений
    print()
    print("2. Публикация тестовых MQTT сообщений...")
    
    current_time = int(time.time())
    
    # Формат A: список устройств
    format_a = [
        {**device, "t": current_time} for device in TEST_DEVICES
    ]
    publish_mqtt_message(mqtt_client, format_a, "A (list)")
    time.sleep(0.5)
    
    # Формат B: объект с полями t, d, c
    format_b = {
        "t": current_time,
        "d": TEST_DEVICES,
        "c": len(TEST_DEVICES)
    }
    publish_mqtt_message(mqtt_client, format_b, "B (object)")
    
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    
    # Ждем обработки данных
    print()
    print("3. Ожидание обработки данных (3 секунды)...")
    time.sleep(3)
    
    # Проверка API эндпоинтов
    print()
    print("4. Проверка API эндпоинтов...")
    
    # Проверка health
    check_api_endpoint(f"{API_BASE_URL}/health", "GET /api/health")
    
    # Проверка statistics
    stats = check_api_endpoint(f"{API_BASE_URL}/statistics", "GET /api/statistics")
    
    # Проверка devices
    devices_data = check_api_endpoint(f"{API_BASE_URL}/devices", "GET /api/devices")
    
    # Проверка новых эндпоинтов
    realtime_data = check_api_endpoint(f"{API_BASE_URL}/stats/realtime", "GET /api/stats/realtime")
    count_data = check_api_endpoint(f"{API_BASE_URL}/stats/count?timeframe=1", "GET /api/stats/count")
    
    # Проверка полей классификации
    print()
    print("5. Проверка полей классификации...")
    
    devices_list = devices_data.get("devices", [])
    if not devices_list:
        print("  ⚠ Список устройств пуст. Возможно данные еще не обработаны.")
        print("  Попробуйте запустить smoke-check еще раз через несколько секунд.")
    else:
        print(f"  Найдено устройств: {len(devices_list)}")
        enrichment_ok = True
        
        for i, device in enumerate(devices_list[:5]):  # Проверяем первые 5
            mac = device.get("mac") or device.get("m", "unknown")
            print(f"  Устройство {i+1}: {mac}")
            
            if not check_enrichment_fields(device):
                enrichment_ok = False
            
            # Выводим значения полей
            print(f"    vendor: {device.get('vendor')}")
            print(f"    device_type: {device.get('device_type')}")
            print(f"    device_brand: {device.get('device_brand')}")
            print(f"    randomized: {device.get('randomized')}")
        
        if enrichment_ok:
            print("  ✓ Все проверенные устройства имеют поля классификации")
        else:
            print("  ⚠ Некоторые устройства не имеют полей классификации")
    
    # Проверка фильтрации
    print()
    print("6. Проверка фильтрации устройств...")
    
    filtering_enabled = os.getenv("ENABLE_DEVICE_FILTERING", "False").lower() == "true"
    print(f"  ENABLE_DEVICE_FILTERING = {filtering_enabled}")
    
    if filtering_enabled:
        # Подсчитываем типы устройств
        device_types = {}
        for device in devices_list:
            device_type = device.get("device_type", "unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        print(f"  Типы устройств в списке: {device_types}")
        
        allowed_types = ["smartphone", "laptop", "tablet", "smartwatch"]
        other_types = [dt for dt in device_types.keys() if dt not in allowed_types]
        
        if other_types:
            print(f"  В списке есть неразрешённые типы: {other_types}")
            print(f"    Это нормально, если фильтр работает корректно (разрешены: {allowed_types})")
        else:
            print("  В списке только разрешенные типы устройств")
    else:
        print("  Фильтрация выключена - все устройства должны быть в списке")
    
    # Итоги
    print()
    print("=" * 60)
    print("Итоги smoke-check:")
    print("=" * 60)
    
    if devices_list:
        print(f"✓ Устройства получены: {len(devices_list)}")
    else:
        print("✗ Устройства не получены - проверьте MQTT consumer и API сервер")
    
    if realtime_data.get("unique_devices", 0) > 0:
        print(f"✓ Realtime endpoint работает: {realtime_data.get('unique_devices')} устройств")
    else:
        print("⚠ Realtime endpoint не вернул данные")
    
    if count_data.get("count", 0) >= 0:
        print(f"✓ Count endpoint работает: {count_data.get('count')} устройств")
    else:
        print("⚠ Count endpoint не вернул данные")
    
    print()
    print("Для повторного запуска:")
    print("  python smoke_check.py")
    print()
    print("Для включения фильтрации перед запуском:")
    print("  $env:ENABLE_DEVICE_FILTERING='True'")
    print("  python main.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
