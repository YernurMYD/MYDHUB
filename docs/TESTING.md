# Инструкция по тестированию системы

## 1. Запуск сервера

```powershell
# Убедитесь, что MQTT брокер (Mosquitto) запущен
python backend/main.py
```

Ожидаемый вывод:
```
Запуск сервиса Wi-Fi мониторинга...
Подключено к MQTT брокеру localhost:1883
Подписка на топик: wifi/probes
MQTT Consumer запущен
API запущен на http://0.0.0.0:5000
Сервис Wi-Fi мониторинга запущен
```

## 2. Автоматический smoke-check

В другом терминале:

```powershell
python tests/smoke_check.py
```

Скрипт автоматически:
- Подключится к MQTT брокеру
- Опубликует тестовые сообщения (оба формата JSON)
- Проверит все API-эндпоинты
- Проверит наличие полей классификации (vendor, device_type, device_brand, randomized)
- Покажет итоги

## 3. Проверка всех компонентов

```powershell
python tests/check_system.py
```

Проверяет: MQTT брокер, MQTT подключение, API сервер, API endpoints.

## 4. Ручная проверка API

```powershell
# Здоровье
curl http://localhost:5000/api/health

# Статистика
curl http://localhost:5000/api/statistics

# Устройства (с полями классификации)
curl http://localhost:5000/api/devices

# Сводка метрик
curl http://localhost:5000/api/stats/summary

# Данные реального времени
curl http://localhost:5000/api/stats/realtime

# Подсчёт устройств за период
curl "http://localhost:5000/api/stats/count?timeframe=1h"

# Временной ряд
curl "http://localhost:5000/api/stats/devices_timeseries?timeframe=1h"
```

## 5. Проверка классификации

Все устройства в `/api/devices` должны иметь заполненные поля:

| Поле | Описание | Примеры |
|------|----------|---------|
| `vendor` | Производитель | `Apple`, `Samsung`, `Intel`, `null` |
| `device_type` | Тип | `smartphone`, `laptop`, `other` |
| `device_brand` | Бренд | `apple`, `samsung`, `null` |
| `randomized` | Рандомизация MAC | `true` / `false` |

**Пример ответа:**
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

## 6. Проверка фильтрации

**Без фильтрации (по умолчанию):**
```powershell
python backend/main.py
# Все устройства сохраняются и возвращаются API
```

**С фильтрацией:**
```powershell
$env:ENABLE_DEVICE_FILTERING="True"
python backend/main.py
# Только smartphone и laptop в API
```

## 7. Проверка форматов MQTT

Система поддерживает оба формата:

**Формат A (массив):**
```json
[
  {"m":"00:1e:c2:aa:bb:cc","r":-63,"t":1700000000,"x":0},
  {"m":"00:12:fb:aa:bb:cc","r":-70,"t":1700000000,"x":0}
]
```

**Формат B (объект с полем d -- используется scanner.sh):**
```json
{
  "t": 1700000000,
  "d": [
    {"m":"00:1e:c2:aa:bb:cc","r":-63,"x":0},
    {"m":"00:12:fb:aa:bb:cc","r":-70,"x":0}
  ],
  "c": 2
}
```

## 8. Тестирование фронтенда

```powershell
cd frontend
npm start
```

Откройте http://localhost:3000 и проверьте:
- Карточки метрик отображают числа
- График рисуется при наличии данных
- Таблица устройств показывает MAC, RSSI, vendor, type
- Селектор периода переключает timeframe (1ч, 6ч, 12ч, 1д, 30д)

## Устранение проблем при тестировании

### Устройства не появляются в API
1. MQTT брокер запущен и доступен?
2. Логи сервера -- есть ли сообщения о получении данных?
3. Топик правильный? (`wifi/probes`)
4. Запустите `tests/smoke_check.py` для тестовой публикации

### Поля классификации отсутствуют
1. Убедитесь, что `device_classifier.py` доступен
2. Логи -- должны быть сообщения «обогащено N»
3. Перезапустите сервер

### Фильтрация не работает
1. Проверьте `ENABLE_DEVICE_FILTERING` через env
2. Перезапустите сервер после изменения
