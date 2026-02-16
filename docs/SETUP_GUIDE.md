# Руководство по настройке системы Wi-Fi мониторинга

Подробное руководство по настройке всех компонентов MYDhub.

## Архитектура

```
┌─────────────────┐         MQTT (1883)        ┌─────────────────────────┐
│  Роутер OpenWrt │ ─────────────────────────▶  │  Windows PC             │
│                 │                             │                         │
│  scanner.sh     │                             │  Mosquitto MQTT Broker  │
│  tcpdump        │                             │          ↓              │
│  mosquitto_pub  │                             │  main.py                │
│                 │                             │  ├── MQTT Consumer      │
│                 │                             │  ├── Device Classifier  │
│                 │                             │  ├── In-Memory Storage  │
│                 │                             │  └── Flask API (:5000)  │
└─────────────────┘                             └────────────┬────────────┘
                                                             │ HTTP
                                                             ▼
                                                ┌────────────────────────┐
                                                │  React Dashboard (:3000)│
                                                └────────────────────────┘
```

## Часть 1: Настройка сервера (Windows PC)

### Шаг 1.1: Установка MQTT брокера

**Вариант A: Установка Mosquitto (рекомендуется)**

1. Скачайте Mosquitto для Windows: https://mosquitto.org/download/
2. Установите Mosquitto (включая сервис)
3. Настройте `mosquitto.conf` для приёма внешних подключений:
   ```
   listener 1883 0.0.0.0
   allow_anonymous true
   ```
4. Проверьте, что брокер запущен:
   ```powershell
   Get-Service mosquitto
   netstat -ano | findstr ":1883"
   ```

**Вариант B: Использование Docker**

```powershell
docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto
```

Подробнее: [MQTT_BROKER_SETUP.md](MQTT_BROKER_SETUP.md)

### Шаг 1.2: Настройка Python окружения

1. Убедитесь, что установлен Python 3.7+:
   ```powershell
   python --version
   ```

2. Установите зависимости:
   ```powershell
   pip install -r requirements.txt
   ```

3. Или запустите автоматическую настройку:
   ```powershell
   .\setup_windows.ps1
   ```

### Шаг 1.3: Конфигурация

Настройки в `config.py` (переопределяются через переменные окружения):

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `MQTT_BROKER_HOST` | `localhost` | Адрес MQTT брокера |
| `MQTT_BROKER_PORT` | `1883` | Порт MQTT брокера |
| `MQTT_TOPIC` | `wifi/probes` | Топик подписки |
| `MQTT_CLIENT_ID` | `wifi_consumer` | ID клиента |
| `API_HOST` | `0.0.0.0` | Хост API |
| `API_PORT` | `5000` | Порт API |
| `ENABLE_DEVICE_FILTERING` | `False` | Фильтрация устройств |

### Шаг 1.4: Настройка фильтрации (опционально)

По умолчанию фильтрация выключена. Все устройства обогащаются классификацией (vendor, device_type, device_brand, randomized) и сохраняются.

Для включения фильтрации (только smartphone и laptop):
```powershell
$env:ENABLE_DEVICE_FILTERING="True"
python main.py
```

### Шаг 1.5: Запуск сервера

```powershell
python main.py
```

Сервер запустит:
- MQTT Consumer (приём данных от роутера)
- REST API на http://localhost:5000

**Доступные API эндпоинты:**

| Эндпоинт | Описание |
|----------|----------|
| `GET /api/health` | Проверка работоспособности |
| `GET /api/statistics` | Общая статистика |
| `GET /api/devices?limit=N` | Список устройств с классификацией |
| `GET /api/devices/<mac>` | Устройство по MAC |
| `GET /api/recent?limit=100` | Последние данные |
| `GET /api/dashboard?limit=100` | Данные для дашборда |
| `GET /api/stats/summary` | Сводка метрик (пик, последний замер, всего) |
| `GET /api/stats/realtime` | Данные за последние 60 секунд |
| `GET /api/stats/count?timeframe=1h` | Подсчёт устройств за период |
| `GET /api/stats/devices_timeseries?timeframe=1h` | Временной ряд |
| `POST /api/clear` | Очистка данных (dev) |

Параметр `timeframe`: `1h` | `6h` | `12h` | `1d` | `30d`

### Шаг 1.6: Настройка Firewall

```powershell
# Через скрипт (от имени администратора)
.\setup_firewall.ps1

# Или вручную
New-NetFirewallRule -DisplayName "MQTT Broker" -Direction Inbound -LocalPort 1883 -Protocol TCP -Action Allow
```

## Часть 2: Настройка роутера (OpenWrt)

### Шаг 2.1: Подключение к роутеру

```bash
ssh root@192.168.1.100  # Замените на IP вашего роутера
```

### Шаг 2.2: Установка пакетов

```bash
opkg update
opkg install mosquitto-client tcpdump coreutils-timeout
```

### Шаг 2.3: Копирование файлов

**С компьютера (SCP):**

```powershell
scp -O scanner.sh root@192.168.1.100:/usr/bin/scanner.sh
scp -O router/scanner.conf.example root@192.168.1.100:/etc/scanner.conf
scp -O router/scanner.init root@192.168.1.100:/etc/init.d/scanner
```

**Или через SSH:**

```powershell
Get-Content scanner.sh -Raw | ssh root@192.168.1.100 "cat > /usr/bin/scanner.sh"
Get-Content router/scanner.conf.example -Raw | ssh root@192.168.1.100 "cat > /etc/scanner.conf"
Get-Content router/scanner.init -Raw | ssh root@192.168.1.100 "cat > /etc/init.d/scanner"
```

### Шаг 2.4: Настройка конфигурации

На роутере отредактируйте `/etc/scanner.conf`:

```bash
vi /etc/scanner.conf
```

**Обязательно:** замените `MQTT_HOST` на IP вашего Windows PC.

Параметры конфигурации:

| Параметр | Обязательный | Описание |
|----------|-------------|----------|
| `INTERFACE` | да | Monitor интерфейс (`mon0`) |
| `MQTT_HOST` | да | IP Windows PC (`192.168.1.101`) |
| `MQTT_TOPIC` | да | MQTT топик (`wifi/probes`) |
| `CYCLE_TIME` | нет | Интервал отправки, сек (по умолчанию `600`) |
| `HOME_CHANNEL` | нет | Рабочий канал Wi-Fi (авто) |
| `NETWORK_SETTLE_TIME` | нет | Ожидание после channel hop (по умолчанию `15`) |
| `HOST_WAIT_TIMEOUT` | нет | Макс. ожидание хоста (по умолчанию `120`) |
| `MQTT_RETRIES` | нет | Попытки отправки (по умолчанию `5`) |
| `BUFFER_MAX` | нет | Макс. буфер (по умолчанию `10`) |

### Шаг 2.5: Установка прав и настройка интерфейса

```bash
chmod +x /usr/bin/scanner.sh
chmod +x /etc/init.d/scanner

# Проверить/создать monitor интерфейс
iw dev
iw phy phy0 interface add mon0 type monitor
ifconfig mon0 up
```

### Шаг 2.6: Автозапуск и запуск

```bash
/etc/init.d/scanner enable   # Автозапуск
/etc/init.d/scanner start    # Запуск сейчас
```

### Шаг 2.7: Альтернатива -- автоматическая настройка

```bash
# Скопируйте setup_router.sh на роутер
scp -O router/setup_router.sh root@192.168.1.100:/tmp/
ssh root@192.168.1.100 "chmod +x /tmp/setup_router.sh && /tmp/setup_router.sh"
```

## Часть 3: Фронтенд (React дашборд)

### Шаг 3.1: Установка и запуск

```powershell
cd frontend
npm install
npm start
```

Дашборд откроется на http://localhost:3000

### Шаг 3.2: Настройка URL бэкенда

По умолчанию: `http://localhost:5000/api`

Для изменения создайте `frontend/.env`:
```
REACT_APP_API_URL=http://your-backend-url/api
```

Подробнее: [frontend/INTEGRATION.md](frontend/INTEGRATION.md)

## Часть 4: Проверка работы

### 4.1: Автоматическая проверка

```powershell
# Проверка всех компонентов
python check_system.py

# Smoke-тесты (публикация + проверка API)
python smoke_check.py
```

### 4.2: Проверка MQTT

```powershell
# Подписка на топик
mosquitto_sub -h localhost -t wifi/probes -v
```

Должны появляться JSON-сообщения от роутера каждые 10 минут.

### 4.3: Проверка API

```powershell
curl http://localhost:5000/api/health
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/devices
curl http://localhost:5000/api/stats/summary
curl "http://localhost:5000/api/stats/devices_timeseries?timeframe=1h"
```

### 4.4: Мониторинг логов

**Сервер (Windows PC):** логи в консоли

**Роутер:**
```bash
logread | grep scanner
/etc/init.d/scanner status
```

## Устранение проблем

См. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Безопасность

1. **MQTT аутентификация:** Для production настройте пароль в Mosquitto
2. **Firewall:** Ограничьте доступ к порту 1883 только с IP роутера
3. **Шифрование:** Для production используйте MQTTS (MQTT over TLS)
