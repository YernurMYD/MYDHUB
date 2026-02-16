#!/usr/bin/env python3
"""
Скрипт для проверки получения MQTT сообщений из топика wifi/probes
Использует paho-mqtt библиотеку
"""
import sys
import time
import json
import paho.mqtt.client as mqtt

# Настройки
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "wifi/probes"  # Правильный топик для scanner

# Callback при подключении
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[OK] Connected to MQTT broker {MQTT_HOST}:{MQTT_PORT}")
        print(f"[OK] Subscribed to topic: {MQTT_TOPIC}")
        print("")
        print("Waiting for messages from scanner...")
        print("Make sure scanner is running on router:")
        print("  ssh root@192.168.1.100")
        print("  /etc/init.d/scanner status")
        print("")
        print("Press Ctrl+C to stop")
        print("")
    else:
        print(f"[ERROR] Failed to connect. Return code: {rc}")
        sys.exit(1)

# Callback при получении сообщения
def on_message(client, userdata, msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Topic: {msg.topic}")
    
    try:
        payload = msg.payload.decode('utf-8')
        print(f"         Raw message: {payload}")
        
        # Попытка распарсить JSON
        try:
            data = json.loads(payload)
            device_count = data.get('c', 0)
            devices = data.get('d', [])
            msg_time = data.get('t', 0)
            
            print(f"         Timestamp: {msg_time}")
            print(f"         Device count: {device_count}")
            
            if device_count > 0:
                print(f"         Devices found:")
                for i, device in enumerate(devices[:5], 1):  # Показываем первые 5
                    mac = device.get('m', 'unknown')
                    rssi = device.get('r', 0)
                    randomized = device.get('x', 0)
                    print(f"           {i}. MAC: {mac}, RSSI: {rssi} dBm, Randomized: {randomized}")
                if len(devices) > 5:
                    print(f"           ... and {len(devices) - 5} more")
            else:
                print(f"         [INFO] No devices in this message (c=0)")
                print(f"         Scanner is working but no devices detected nearby")
        except json.JSONDecodeError:
            print(f"         [WARNING] Message is not valid JSON")
    except Exception as e:
        print(f"         [ERROR] Failed to process message: {e}")
    
    print("")

# Callback при отключении
def on_disconnect(client, userdata, rc, properties=None):
    print("\n[INFO] Disconnected from MQTT broker")

# Создание клиента
try:
    # Поддержка paho-mqtt v1 и v2
    if hasattr(mqtt, "CallbackAPIVersion"):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="wifi_probes_receiver")
    else:
        client = mqtt.Client(client_id="wifi_probes_receiver")
except Exception as e:
    print(f"[ERROR] Failed to create MQTT client: {e}")
    sys.exit(1)

# Установка callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Подключение и подписка
try:
    print("========================================")
    print("Wi-Fi Probes MQTT Receiver")
    print("========================================")
    print("")
    print(f"Connecting to {MQTT_HOST}:{MQTT_PORT}...")
    
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC, qos=0)
    
    # Бесконечный цикл ожидания сообщений
    client.loop_forever()
    
except KeyboardInterrupt:
    print("\n[INFO] Stopping...")
    client.disconnect()
    print("[OK] Disconnected")
except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)
