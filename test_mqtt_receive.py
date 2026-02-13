#!/usr/bin/env python3
"""
Скрипт для проверки получения MQTT сообщений на Windows PC
Использует paho-mqtt библиотеку
"""
import sys
import time
import paho.mqtt.client as mqtt

# Настройки
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "test"

# Callback при подключении
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[OK] Connected to MQTT broker {MQTT_HOST}:{MQTT_PORT}")
        print(f"[OK] Subscribed to topic: {MQTT_TOPIC}")
        print("")
        print("Waiting for messages...")
        print("Send message from router with:")
        print("  mosquitto_pub -h 192.168.1.101 -t test -m 'test'")
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
    print(f"         Message: {msg.payload.decode('utf-8')}")
    print("")

# Callback при отключении
def on_disconnect(client, userdata, rc, properties=None):
    print("\n[INFO] Disconnected from MQTT broker")

# Создание клиента
try:
    # Поддержка paho-mqtt v1 и v2
    if hasattr(mqtt, "CallbackAPIVersion"):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="test_receiver")
    else:
        client = mqtt.Client(client_id="test_receiver")
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
    print("MQTT Message Receiver Test")
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
