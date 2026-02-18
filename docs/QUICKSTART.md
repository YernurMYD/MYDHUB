# Быстрый старт

Краткая инструкция по запуску системы Wi-Fi мониторинга MYDhub.

## На сервере (Windows PC)

### 1. Установка MQTT брокера

**Вариант A: Mosquitto**
- Скачайте: https://mosquitto.org/download/
- Настройте `mosquitto.conf`: `listener 1883 0.0.0.0` + `allow_anonymous true`
- Запустите сервис

**Вариант B: Docker**
```powershell
docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto
```

### 2. Установка Python-зависимостей

```powershell
cd c:\Yernur\MYD\integration\MYDhub

# Автоматическая настройка
.\scripts\setup_windows.ps1

# Или вручную
pip install -r backend/requirements.txt
```

### 3. Запуск сервера

```powershell
.\scripts\start_server.ps1
# Или:
python backend/main.py
```

Сервер будет доступен на:
- API: http://localhost:5000
- MQTT: localhost:1883

### 4. Запуск фронтенда

```powershell
cd frontend
npm install
npm start
```

Дашборд: http://localhost:3000

### 5. Проверка

```powershell
python tests/check_system.py

curl http://localhost:5000/api/health
curl http://localhost:5000/api/stats/summary
curl "http://localhost:5000/api/stats/devices_timeseries?timeframe=1h"
```

## На роутере (OpenWrt)

### 1. Установка пакетов

```bash
opkg update
opkg install mosquitto-client tcpdump coreutils-timeout
```

### 2. Копирование файлов (с ПК)

```powershell
scp -O scanner.sh root@192.168.1.100:/usr/bin/scanner.sh
scp -O router/scanner.conf.example root@192.168.1.100:/etc/scanner.conf
scp -O router/scanner.init root@192.168.1.100:/etc/init.d/scanner
```

### 3. Настройка конфигурации

```bash
ssh root@192.168.1.100
vi /etc/scanner.conf
```

**Обязательно:** замените `MQTT_HOST` на IP вашего Windows PC.

### 4. Настройка и запуск

```bash
chmod +x /usr/bin/scanner.sh
chmod +x /etc/init.d/scanner

iw phy phy0 interface add mon0 type monitor
ifconfig mon0 up

/etc/init.d/scanner enable
/etc/init.d/scanner start
```

## Проверка работы

### На Windows PC

```powershell
# Подписка на MQTT топик
mosquitto_sub -h localhost -t wifi/probes -v

# API
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/devices
curl http://localhost:5000/api/stats/summary
```

### На роутере

```bash
/etc/init.d/scanner status
logread | grep scanner
```

## Устранение проблем

### Данные не приходят
1. Ping: `ping <IP_PC>` с роутера
2. MQTT: `mosquitto_pub -h <IP_PC> -t test -m "test"` с роутера
3. Firewall: `.\scripts\setup_firewall.ps1` на PC
4. Конфиг: `cat /etc/scanner.conf` на роутере

### API не отвечает
1. Сервер запущен? `python backend/main.py`
2. Порт? `netstat -an | findstr 5000`
3. Логи в консоли

Подробнее: [SETUP_GUIDE.md](SETUP_GUIDE.md) | [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
