# MYDhub -- Wi-Fi Мониторинг

Система мониторинга Wi-Fi устройств через анализ Probe Request пакетов. Роутер OpenWrt перехватывает Wi-Fi запросы, отправляет данные через MQTT на сервер, где Python-бэкенд обрабатывает, классифицирует устройства и отдаёт данные через REST API. React-дашборд визуализирует статистику в реальном времени.

## Архитектура

```
┌─────────────────┐         MQTT (1883)        ┌─────────────────────────┐
│  Роутер OpenWrt │ ─────────────────────────▶  │  Windows PC             │
│                 │                             │                         │
│  scanner.sh     │                             │  Mosquitto (MQTT Broker)│
│  tcpdump        │                             │          ↓              │
│  mosquitto_pub  │                             │  MQTT Consumer          │
│                 │                             │  Device Classifier      │
│                 │                             │  In-Memory Storage      │
│                 │                             │  Flask REST API (:5000) │
└─────────────────┘                             └────────────┬────────────┘
                                                             │ HTTP
                                                             ▼
                                                ┌────────────────────────┐
                                                │  React Dashboard (:3000)│
                                                │                        │
                                                │  Метрики, График,      │
                                                │  Таблица устройств     │
                                                └────────────────────────┘
```

## Структура проекта

```
MYDhub/
├── backend/                 # Python backend (Flask API + MQTT Consumer)
│   ├── main.py              # Точка входа: MQTT Consumer + API
│   ├── config.py            # Конфигурация (env vars)
│   ├── mqtt_consumer.py     # Приём и обработка MQTT-сообщений
│   ├── dashboard_api.py     # Flask REST API
│   ├── storage.py           # Потокобезопасное in-memory хранилище
│   ├── device_classifier.py # Классификация устройств по OUI
│   └── requirements.txt     # Python зависимости
│
├── frontend/                # React Dashboard
│   ├── src/
│   │   ├── components/      # UI компоненты
│   │   ├── pages/           # Страницы (Dashboard, Devices, Users, Settings)
│   │   ├── services/        # API клиент
│   │   └── utils/           # Утилиты
│   └── public/              # Статические файлы
│
├── router/                  # Конфигурация OpenWrt роутера
│   ├── scanner.sh           # Скрипт сканирования Wi-Fi
│   ├── scanner.conf.example # Пример конфигурации
│   ├── scanner.init         # Init-скрипт для автозапуска (procd)
│   ├── setup_router.sh      # Автоматическая настройка роутера
│   ├── diagnose_mqtt.sh     # Диагностика MQTT на роутере
│   └── README.md            # Инструкция по настройке роутера
│
├── scripts/                 # Скрипты запуска и настройки
│   ├── start_server.ps1     # Запуск сервера (PowerShell)
│   ├── start_server.bat     # Запуск сервера (CMD)
│   ├── setup_windows.ps1    # Настройка Windows-окружения
│   ├── setup_firewall.ps1   # Настройка Windows Firewall
│   └── start_mosquitto.ps1  # Запуск Mosquitto брокера
│
├── tests/                   # Тесты и проверки
│   ├── check_system.py      # Проверка работоспособности (MQTT + API)
│   ├── smoke_check.py       # Smoke-тесты (публикация + проверка)
│   ├── test_mqtt_wifi_probes.py  # Тест приёма MQTT сообщений
│   └── test_mqtt_receive.py     # Тест MQTT подключения
│
├── docs/                    # Документация
│   ├── SETUP_GUIDE.md       # Подробное руководство по настройке
│   ├── QUICKSTART.md        # Краткая инструкция
│   ├── MQTT_BROKER_SETUP.md # Настройка MQTT брокера
│   ├── HOW_TO_TEST_MQTT.md  # Тестирование MQTT
│   ├── TESTING.md           # Инструкция по тестированию
│   ├── TROUBLESHOOTING.md   # Устранение проблем
│   ├── NETWORK_INFO.md      # Сетевая конфигурация
│   └── ЗАПУСК_СИСТЕМЫ.md    # Пошаговый чек-лист запуска
│
├── .gitignore
├── .gitattributes
└── README.md
```

## Требования

- Python 3.7+
- Node.js 16+ (для фронтенда)
- Windows PC
- MQTT брокер (Mosquitto)
- Роутер OpenWrt с поддержкой monitor mode

## Быстрый старт

> Подробные инструкции: **[docs/ЗАПУСК_СИСТЕМЫ.md](docs/ЗАПУСК_СИСТЕМЫ.md)** | **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** | **[docs/QUICKSTART.md](docs/QUICKSTART.md)**

### 1. Установка зависимостей

```powershell
pip install -r backend/requirements.txt
```

### 2. Конфигурация (опционально)

Переменные окружения (или значения по умолчанию из `backend/config.py`):

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `MQTT_BROKER_HOST` | `localhost` | Адрес MQTT брокера |
| `MQTT_BROKER_PORT` | `1883` | Порт MQTT брокера |
| `MQTT_TOPIC` | `wifi/probes` | Топик для подписки |
| `MQTT_CLIENT_ID` | `wifi_consumer` | ID MQTT клиента |
| `API_HOST` | `0.0.0.0` | Хост для API |
| `API_PORT` | `5000` | Порт для API |
| `ENABLE_DEVICE_FILTERING` | `False` | Фильтрация по типу устройств |

### 3. Запуск сервера

```powershell
# Через скрипт
.\scripts\start_server.ps1

# Или напрямую
python backend/main.py
```

### 4. Запуск фронтенда

```powershell
cd frontend
npm install
npm start
```

Дашборд: http://localhost:3000 | API: http://localhost:5000

## Формат данных MQTT

Система поддерживает два формата входящих сообщений:

### Формат A: Прямой массив
```json
[
  {"m": "aa:bb:cc:dd:ee:ff", "r": -63, "t": 1700000000, "x": 0}
]
```

### Формат B: Объект (используется scanner.sh)
```json
{
  "t": 1700000000,
  "d": [
    {"m": "aa:bb:cc:dd:ee:ff", "r": -63, "x": 0}
  ],
  "c": 1
}
```

| Поле | Описание |
|------|----------|
| `m` | MAC-адрес устройства |
| `r` | RSSI (сила сигнала, dBm) |
| `t` | Unix timestamp |
| `x` | Флаг рандомизированного MAC (0/1) |
| `c` | Количество устройств в батче |

## Классификация устройств

Все устройства автоматически обогащаются классификацией по OUI (первые 3 октета MAC):

| Поле | Описание | Примеры значений |
|------|----------|------------------|
| `vendor` | Производитель | `Apple`, `Samsung`, `Intel`, `Dell`, `HP`, `Lenovo`, `null` |
| `device_type` | Тип устройства | `smartphone`, `laptop`, `other` |
| `device_brand` | Бренд | `apple`, `samsung`, `null` |
| `randomized` | Рандомизированный MAC | `true` / `false` |

Классификация выполняется **всегда**, независимо от настройки фильтрации. При `ENABLE_DEVICE_FILTERING=True` в хранилище попадают только `smartphone` и `laptop`.

## API Endpoints

Базовый URL: `http://localhost:5000`

### GET /api/health
Проверка работоспособности.

**Ответ:** `{"status": "ok"}`

### GET /api/statistics
Общая статистика системы.

**Ответ:**
```json
{
  "total_messages": 100,
  "total_devices": 42,
  "current_devices": 42,
  "timestamps_count": 100,
  "first_message_time": "2026-01-01T00:00:00",
  "last_message_time": "2026-01-01T12:00:00",
  "peak_snapshot_count": 35,
  "last_snapshot_count": 28
}
```

### GET /api/devices?limit=N
Список устройств с классификацией (сортировка по `last_seen` desc).

**Ответ:**
```json
{
  "devices": [
    {
      "mac": "00:1e:c2:aa:bb:cc",
      "rssi": -63,
      "first_seen": 1700000000,
      "last_seen": 1700003600,
      "count": 10,
      "best_rssi": -50,
      "latest_rssi": -63,
      "vendor": "Apple",
      "device_type": "smartphone",
      "device_brand": "apple",
      "randomized": false
    }
  ],
  "count": 1
}
```

### GET /api/devices/\<mac\>
Информация об устройстве по MAC-адресу.

### GET /api/recent?limit=100
Последние данные (временные метки с устройствами).

### GET /api/dashboard?limit=100
Агрегированные данные для дашборда (статистика + топ-20 устройств + последняя активность).

### GET /api/stats/summary
Сводка метрик для карточек дашборда.

**Ответ:**
```json
{
  "peak_all_time": 35,
  "last_snapshot": 28,
  "total_unique": 42
}
```

### GET /api/stats/realtime
Устройства за последние 60 секунд.

**Ответ:**
```json
{
  "unique_devices": 15,
  "devices": [
    {
      "mac": "aa:bb:cc:dd:ee:ff",
      "rssi": -65,
      "timestamp": "2026-01-01T12:00:00Z",
      "is_random": false
    }
  ]
}
```

### GET /api/stats/count?timeframe=1h
Количество уникальных устройств за период.

**Параметр `timeframe`:** `1h` | `6h` | `12h` | `1d` | `30d`

### GET /api/stats/devices_timeseries?timeframe=1h
Временной ряд: количество уникальных устройств по бакетам времени.

**Параметр `timeframe`:** `1h` | `6h` | `12h` | `1d` | `30d`

### POST /api/clear
Очистка всех данных (только для разработки).

## Проверка системы

```powershell
python tests/check_system.py   # Проверка MQTT + API
python tests/smoke_check.py    # Smoke-тесты (публикация + проверка)
```

## Особенности

- **Классификация устройств** -- автоматическое определение типа по OUI (Apple, Samsung, Intel и др.)
- **Потокобезопасность** -- все операции с хранилищем защищены блокировками
- **Два формата MQTT** -- поддержка прямого массива и объекта с полем `d`
- **Локальный буфер** -- scanner сохраняет данные при недоступности MQTT и досылает позже
- **Channel hopping** -- сканирование каналов 1, 6, 11 с автоматическим восстановлением сети
- **Совместимость paho-mqtt** -- поддержка v1 и v2 API
- **CORS** -- настроен для работы с React-фронтендом
- **Лимиты хранилища** -- до 10000 уникальных устройств, до 1000 временных меток

## Документация

| Документ | Описание |
|----------|----------|
| [docs/ЗАПУСК_СИСТЕМЫ.md](docs/ЗАПУСК_СИСТЕМЫ.md) | Пошаговый чек-лист запуска всей системы |
| [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Подробное руководство по настройке |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | Краткая инструкция |
| [docs/MQTT_BROKER_SETUP.md](docs/MQTT_BROKER_SETUP.md) | Настройка MQTT брокера |
| [docs/HOW_TO_TEST_MQTT.md](docs/HOW_TO_TEST_MQTT.md) | Тестирование MQTT |
| [docs/TESTING.md](docs/TESTING.md) | Инструкция по тестированию |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Устранение проблем |
| [docs/NETWORK_INFO.md](docs/NETWORK_INFO.md) | Сетевая конфигурация |
| [router/README.md](router/README.md) | Настройка роутера |
| [frontend/INTEGRATION.md](frontend/INTEGRATION.md) | Интеграция фронтенда с бэкендом |

## Лицензия

Проект для внутреннего использования.
