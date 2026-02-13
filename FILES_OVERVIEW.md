# Обзор файлов проекта MYDhub

## Структура проекта

```
MYDhub/
├── main.py                        # Точка входа: MQTT Consumer + Flask API
├── mqtt_consumer.py               # MQTT Consumer (приём и парсинг данных)
├── dashboard_api.py               # Flask REST API для дашборда
├── storage.py                     # Потокобезопасное in-memory хранилище
├── config.py                      # Конфигурация (MQTT, API, фильтрация)
├── device_classifier.py           # Классификация устройств по MAC OUI
├── scanner.sh                     # Wi-Fi сканер для роутера OpenWrt
├── requirements.txt               # Python-зависимости
│
├── router/                        # Файлы для настройки роутера
│   ├── README.md                  # Инструкции по настройке роутера
│   ├── scanner.conf.example       # Пример конфигурации сканера
│   ├── scanner.init               # Init-скрипт для автозапуска (procd)
│   ├── setup_router.sh            # Автоматическая настройка роутера
│   └── diagnose_mqtt.sh           # Диагностика MQTT на роутере
│
├── frontend/                      # React-дашборд
│   ├── package.json               # npm-зависимости
│   ├── INTEGRATION.md             # Документация интеграции с бэкендом
│   ├── public/
│   │   └── index.html             # HTML-шаблон
│   └── src/
│       ├── App.css                # Глобальные стили
│       ├── services/
│       │   └── api.js             # API-клиент (axios)
│       ├── pages/
│       │   └── Dashboard/
│       │       ├── Dashboard.js   # Главная страница дашборда
│       │       └── Dashboard.css  # Стили дашборда
│       └── components/
│           ├── Header/            # Шапка дашборда
│           ├── MetricCard/        # Карточка метрики
│           ├── DevicesTable/      # Таблица устройств
│           ├── RSSIChart/         # График устройств по времени
│           └── TimeframeSelector/ # Селектор периода
│
├── Скрипты (Windows)
│   ├── setup_windows.ps1          # Автоматическая настройка Windows
│   ├── start_server.ps1           # Запуск сервера (PowerShell)
│   ├── start_server.bat           # Запуск сервера (CMD)
│   ├── setup_firewall.ps1         # Настройка Windows Firewall (порт 1883)
│   ├── start_mosquitto.ps1        # Запуск Mosquitto брокера
│   ├── check_mosquitto_config.ps1 # Проверка конфигурации Mosquitto
│   ├── check_mqtt_connection.ps1  # Тестирование MQTT-соединения
│   ├── test_mqtt_receive.ps1      # Тест приёма MQTT-сообщений
│   ├── create_config_via_ssh.ps1  # Создание конфига на роутере через SSH
│   ├── copy_config_to_router.ps1  # Копирование конфига на роутер
│   ├── diagnose_server.ps1        # Диагностика сервера
│   └── fix_server.ps1             # Исправление проблем сервера
│
├── Скрипты тестирования
│   ├── check_system.py            # Проверка всех компонентов системы
│   ├── smoke_check.py             # Smoke-тесты (публикация + проверка API)
│   ├── test_mqtt_wifi_probes.py   # Тест MQTT на топик wifi/probes
│   ├── test_mqtt_receive.py       # Тест приёма MQTT (Python)
│   └── VERIFY_ROUTER_CONFIG.sh    # Проверка конфигурации роутера
│
└── Документация
    ├── README.md                  # Главная документация проекта
    ├── ЗАПУСК_СИСТЕМЫ.md          # Пошаговый чек-лист запуска
    ├── SETUP_GUIDE.md             # Подробное руководство по настройке
    ├── QUICKSTART.md              # Краткая инструкция
    ├── FILES_OVERVIEW.md          # Этот файл
    ├── MQTT_BROKER_SETUP.md       # Настройка MQTT брокера
    ├── HOW_TO_TEST_MQTT.md        # Тестирование MQTT
    ├── TESTING.md                 # Инструкция по тестированию
    ├── TROUBLESHOOTING.md         # Устранение проблем
    └── NETWORK_INFO.md            # Сетевая конфигурация
```

## Бэкенд (Python)

### main.py -- Точка входа
Запускает `WiFiMonitoringService`:
- Создаёт `WiFiDataStorage`
- Запускает `MQTTConsumer` (приём данных)
- Запускает Flask API в отдельном потоке
- Обработка сигналов SIGINT/SIGTERM для graceful shutdown

### mqtt_consumer.py -- MQTT Consumer
Принимает данные от роутера через MQTT:
- Поддержка двух форматов JSON (массив и объект с полем `d`)
- Обогащение данных классификацией через `device_classifier.py`
- Опциональная фильтрация по типу устройств
- Совместимость с paho-mqtt v1 и v2
- Экспоненциальная задержка при переподключении (до 10 попыток)

### dashboard_api.py -- Flask REST API
REST API для дашборда с эндпоинтами:
- `/api/health` -- проверка работоспособности
- `/api/statistics` -- общая статистика
- `/api/devices` -- список устройств с классификацией
- `/api/devices/<mac>` -- устройство по MAC
- `/api/recent` -- последние данные
- `/api/dashboard` -- агрегированные данные
- `/api/stats/summary` -- сводка метрик
- `/api/stats/realtime` -- данные за 60 секунд
- `/api/stats/count` -- подсчёт устройств за период
- `/api/stats/devices_timeseries` -- временной ряд
- `/api/clear` -- очистка данных (dev)

### storage.py -- In-Memory хранилище
Потокобезопасное хранилище:
- До 10000 уникальных устройств
- До 1000 временных меток (deque)
- Поля устройства: mac, first_seen, last_seen, count, best_rssi, latest_rssi, vendor, device_type, device_brand, randomized
- Отслеживание peak_snapshot_count и last_snapshot_count

### config.py -- Конфигурация
Переменные окружения с значениями по умолчанию:
- MQTT: broker host/port, topic, client_id
- API: host, port
- Хранение: max devices (10000), max timestamps (1000)
- Фильтрация: ENABLE_DEVICE_FILTERING, ALLOWED_DEVICE_TYPES

### device_classifier.py -- Классификация устройств
Классификация по OUI (первые 3 октета MAC):
- Поддержка вендоров: Apple, Samsung, Intel, Dell, HP, Lenovo
- Типы: smartphone (Apple, Samsung), laptop (Intel, Dell, HP, Lenovo), other
- Определение рандомизированного MAC (LAA bit)

## Роутер (OpenWrt)

### scanner.sh -- Wi-Fi сканер
Основной скрипт сканирования:
- Перехват Probe Request через tcpdump
- Channel hopping (каналы 1, 6, 11)
- Агрегация данных с дедупликацией по MAC
- Отправка JSON в MQTT каждые CYCLE_TIME секунд (по умолчанию 600 = 10 мин)
- Локальный буфер при недоступности MQTT
- Автоматическое восстановление сети после channel hopping
- Экспоненциальная задержка при повторных попытках отправки

### router/scanner.conf.example -- Конфигурация
Параметры сканера: INTERFACE, MQTT_HOST, MQTT_TOPIC, CYCLE_TIME, HOME_CHANNEL, NETWORK_SETTLE_TIME, HOST_WAIT_TIMEOUT, MQTT_RETRIES, BUFFER_MAX

### router/scanner.init -- Init-скрипт
Скрипт автозапуска через procd (OpenWrt).

### router/setup_router.sh -- Автонастройка
Установка пакетов, настройка интерфейса, init-скрипт.

## Фронтенд (React)

### services/api.js -- API-клиент
Axios-клиент для бэкенда:
- `getRealtimeStats()` -- данные реального времени
- `getDeviceTimeseries(timeframe)` -- временной ряд
- `getDevicesCount(timeframe)` -- подсчёт устройств
- `getStatsSummary()` -- сводка метрик
- `getDevices()` -- список устройств

### pages/Dashboard/Dashboard.js -- Дашборд
Главная страница с автообновлением каждые 10 минут:
- Карточки метрик (пик, за период, последний замер)
- Селектор периода (1ч, 6ч, 12ч, 1д, 30д)
- График уникальных устройств во времени (Recharts)
- Таблица устройств с классификацией

## Порядок использования

1. **Установка:** `pip install -r requirements.txt` + `cd frontend && npm install`
2. **Запуск MQTT:** Mosquitto должен слушать на 0.0.0.0:1883
3. **Запуск сервера:** `python main.py` (Consumer + API на :5000)
4. **Запуск фронтенда:** `cd frontend && npm start` (дашборд на :3000)
5. **Настройка роутера:** копирование файлов, настройка `/etc/scanner.conf`
6. **Проверка:** `python check_system.py` или `python smoke_check.py`
