# Интеграция Frontend с Backend

## Архитектура

```
React Dashboard (localhost:3000)
    │
    │ HTTP (axios)
    ▼
Flask REST API (localhost:5000/api)
    │
    ├── /api/stats/summary          → Метрики для карточек
    ├── /api/stats/devices_timeseries → Данные для графика
    ├── /api/stats/count            → Подсчёт устройств за период
    ├── /api/stats/realtime         → Данные за 60 секунд
    └── /api/devices                → Таблица устройств
```

## API-клиент (services/api.js)

Базовый URL: `REACT_APP_API_URL` или `http://localhost:5000/api`

| Функция | Эндпоинт | Описание |
|---------|----------|----------|
| `getStatsSummary()` | `GET /api/stats/summary` | Пик, последний замер, всего уникальных |
| `getDeviceTimeseries(tf)` | `GET /api/stats/devices_timeseries?timeframe=tf` | Временной ряд по бакетам |
| `getDevicesCount(tf)` | `GET /api/stats/count?timeframe=tf` | Уникальных устройств за период |
| `getRealtimeStats()` | `GET /api/stats/realtime` | Устройства за последние 60 секунд |
| `getDevices()` | `GET /api/devices` | Список всех устройств |

Параметр `timeframe`: `1h` | `6h` | `12h` | `1d` | `30d`

## API Endpoints -- формат ответов

### GET /api/stats/summary

```json
{
  "peak_all_time": 35,
  "last_snapshot": 28,
  "total_unique": 42
}
```

### GET /api/stats/devices_timeseries?timeframe=1h

```json
{
  "timeframe": "1h",
  "start_ts": 1700000000,
  "end_ts": 1700003600,
  "bucket_sec": 600,
  "points": [
    {"t": 1700000000, "count": 10},
    {"t": 1700000600, "count": 15}
  ]
}
```

Размер бакета зависит от timeframe:
| Timeframe | Bucket | Точек |
|-----------|--------|-------|
| 1h | 600с (10 мин) | ~6 |
| 6h | 900с (15 мин) | ~24 |
| 12h | 1800с (30 мин) | ~24 |
| 1d | 3600с (1 час) | ~24 |
| 30d | 86400с (1 день) | ~30 |

### GET /api/stats/count?timeframe=1h

```json
{
  "timeframe": "1h",
  "count": 28,
  "start_ts": 1700000000,
  "end_ts": 1700003600
}
```

### GET /api/stats/realtime

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

### GET /api/devices

```json
{
  "devices": [
    {
      "mac": "00:1e:c2:aa:bb:cc",
      "m": "00:1e:c2:aa:bb:cc",
      "rssi": -63,
      "r": -63,
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

Поля `m` и `r` -- для обратной совместимости (дублируют `mac` и `rssi`).

## Классификация устройств

Backend всегда обогащает устройства:

| Поле | Описание | Значения |
|------|----------|----------|
| `vendor` | Производитель по OUI | `Apple`, `Samsung`, `Intel`, `Dell`, `HP`, `Lenovo`, `null` |
| `device_type` | Тип устройства | `smartphone`, `laptop`, `other` |
| `device_brand` | Бренд | `apple`, `samsung`, `null` |
| `randomized` | Рандомизированный MAC | `true` / `false` |

## Фильтрация

- **`ENABLE_DEVICE_FILTERING=False`** (по умолчанию): все устройства сохраняются, все обогащены
- **`ENABLE_DEVICE_FILTERING=True`**: только `smartphone` и `laptop` в storage и API

## Dashboard -- компоненты

| Компонент | Данные | API |
|-----------|--------|-----|
| MetricCard (Пик) | `summary.peak_all_time` | `/api/stats/summary` |
| MetricCard (За период) | `count.count` | `/api/stats/count` |
| MetricCard (Последний) | `summary.last_snapshot` | `/api/stats/summary` |
| RSSIChart | `timeseries.points` | `/api/stats/devices_timeseries` |
| TimeframeSelector | Выбранный период | Управляет timeframe |
| DevicesTable | `devices[]` | `/api/devices` |

Автообновление: каждые 10 минут (600000 мс).

## CORS

Backend разрешает CORS через `flask_cors`:
```python
from flask_cors import CORS
CORS(app)
```

## Настройка URL

По умолчанию: `http://localhost:5000/api`

Для изменения создайте `frontend/.env`:
```
REACT_APP_API_URL=http://your-backend-url/api
```
