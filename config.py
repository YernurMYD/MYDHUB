"""
Конфигурация MQTT consumer и API
"""
import os

# MQTT настройки
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "wifi/probes")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "wifi_consumer")

# API настройки
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

# Настройки хранения
MAX_DEVICES_HISTORY = 10000  # Максимальное количество уникальных устройств в истории
MAX_TIMESTAMPS = 1000  # Максимальное количество временных меток для хранения

# Настройки фильтрации устройств
ENABLE_DEVICE_FILTERING = os.getenv("ENABLE_DEVICE_FILTERING", "False").lower() == "true"
ALLOWED_DEVICE_TYPES = ["smartphone", "laptop"]  # Типы устройств, которые сохраняются
