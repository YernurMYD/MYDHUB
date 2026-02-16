"""
Скрипт для проверки работоспособности системы Wi-Fi мониторинга
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import socket
import requests
from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC,
    API_HOST,
    API_PORT
)

def check_mqtt_broker():
    """Проверка доступности MQTT брокера"""
    print("Проверка MQTT брокера...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((MQTT_BROKER_HOST, MQTT_BROKER_PORT))
        sock.close()
        
        if result == 0:
            print(f"  ✓ MQTT брокер доступен на {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            return True
        else:
            print(f"  ✗ MQTT брокер недоступен на {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            print(f"    Убедитесь, что Mosquitto запущен")
            return False
    except Exception as e:
        print(f"  ✗ Ошибка при проверке MQTT брокера: {e}")
        return False

def check_api_server():
    """Проверка доступности API сервера"""
    print("\nПроверка API сервера...")
    try:
        url = f"http://{API_HOST}:{API_PORT}/api/health"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            print(f"  ✓ API сервер доступен на http://{API_HOST}:{API_PORT}")
            return True
        else:
            print(f"  ✗ API сервер вернул код {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ API сервер недоступен на http://{API_HOST}:{API_PORT}")
        print(f"    Убедитесь, что сервер запущен (python main.py)")
        return False
    except Exception as e:
        print(f"  ✗ Ошибка при проверке API сервера: {e}")
        return False

def check_mqtt_connection():
    """Проверка подключения к MQTT брокеру"""
    print("\nПроверка подключения к MQTT...")
    try:
        import paho.mqtt.client as mqtt
        
        client = mqtt.Client()
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 5)
        client.loop_start()
        
        # Ждем подключения
        import time
        time.sleep(1)
        
        if client.is_connected():
            print(f"  ✓ Успешное подключение к MQTT брокеру")
            print(f"    Топик для подписки: {MQTT_TOPIC}")
            client.loop_stop()
            client.disconnect()
            return True
        else:
            print(f"  ✗ Не удалось подключиться к MQTT брокеру")
            client.loop_stop()
            return False
    except ImportError:
        print(f"  ✗ Библиотека paho-mqtt не установлена")
        print(f"    Установите: pip install paho-mqtt")
        return False
    except Exception as e:
        print(f"  ✗ Ошибка при подключении к MQTT: {e}")
        return False

def check_api_endpoints():
    """Проверка основных API endpoints"""
    print("\nПроверка API endpoints...")
    endpoints = [
        ("/api/health", "Health check"),
        ("/api/statistics", "Statistics"),
        ("/api/devices", "Devices list"),
    ]
    
    all_ok = True
    for endpoint, name in endpoints:
        try:
            url = f"http://{API_HOST}:{API_PORT}{endpoint}"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                print(f"  ✓ {name}: OK")
            else:
                print(f"  ✗ {name}: код {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"  ✗ {name}: ошибка - {e}")
            all_ok = False
    
    return all_ok

def main():
    """Главная функция"""
    print("=" * 50)
    print("Проверка системы Wi-Fi мониторинга")
    print("=" * 50)
    
    results = []
    
    # Проверки
    results.append(("MQTT брокер", check_mqtt_broker()))
    results.append(("MQTT подключение", check_mqtt_connection()))
    results.append(("API сервер", check_api_server()))
    results.append(("API endpoints", check_api_endpoints()))
    
    # Итоги
    print("\n" + "=" * 50)
    print("Результаты проверки:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("Все проверки пройдены успешно!")
        return 0
    else:
        print("Некоторые проверки не пройдены. Проверьте настройки.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
