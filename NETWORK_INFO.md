# Сетевая конфигурация

## IP-адреса устройств

| Устройство | IP | Описание |
|------------|-----|----------|
| Роутер OpenWrt | `192.168.1.100` | Web: http://192.168.1.100/ SSH: `ssh root@192.168.1.100` |
| Windows PC (сервер) | `192.168.1.101` | API: http://192.168.1.101:5000 MQTT: `192.168.1.101:1883` |

## Порты

| Порт | Протокол | Назначение |
|------|----------|-----------|
| 1883 | TCP | MQTT брокер (должен быть открыт в Windows Firewall) |
| 5000 | TCP | Flask REST API |
| 3000 | TCP | React дашборд (dev server) |
| 22 | TCP | SSH (роутер) |

## Конфигурация MQTT

### На роутере (`/etc/scanner.conf`)

```bash
INTERFACE="mon0"
MQTT_HOST="192.168.1.101"   # IP Windows PC
MQTT_TOPIC="wifi/probes"
CYCLE_TIME=600
```

### На Windows PC (`config.py`)

```python
MQTT_BROKER_HOST = "localhost"   # Consumer подключается к локальному брокеру
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "wifi/probes"
```

## Проверка подключения

### Windows PC → Роутер

```powershell
Test-Connection -ComputerName 192.168.1.100
ssh root@192.168.1.100
```

### Роутер → Windows PC

```bash
ping 192.168.1.101
mosquitto_pub -h 192.168.1.101 -t test -m "test"
```

### Проверка портов

```powershell
# MQTT брокер
Test-NetConnection -ComputerName localhost -Port 1883
netstat -ano | findstr ":1883"

# Flask API
Test-NetConnection -ComputerName localhost -Port 5000
```

## Поток данных

```
Роутер (192.168.1.100)
    │ scanner.sh → mosquitto_pub
    │ MQTT (порт 1883)
    ▼
Windows PC (192.168.1.101)
    │ Mosquitto MQTT Broker (0.0.0.0:1883)
    │       ↓
    │ mqtt_consumer.py → storage.py → dashboard_api.py
    │ Flask API (0.0.0.0:5000)
    │       ↓ HTTP
    ▼
Браузер (localhost:3000)
    React Dashboard
```
