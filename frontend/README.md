# Wi-Fi Analytics Dashboard

Коммерческий web-дашборд для Wi-Fi analytics SaaS. Single Page Application на React.

## Структура проекта

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/          # Переиспользуемые компоненты
│   │   ├── Header/
│   │   ├── MetricCard/
│   │   ├── TimeframeSelector/
│   │   ├── RSSIChart/
│   │   └── DevicesTable/
│   ├── pages/               # Страницы приложения
│   │   └── Dashboard/
│   ├── services/            # API сервисы
│   │   └── api.js
│   ├── App.js
│   ├── App.css
│   └── index.js
├── package.json
└── README.md
```

## Установка и запуск

### Требования
- Node.js 16+ 
- npm или yarn

### Установка зависимостей

```bash
cd frontend
npm install
```

### Настройка API

Создайте файл `.env` в корне папки `frontend`:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

### Запуск в режиме разработки

```bash
npm start
```

Приложение откроется на `http://localhost:3000`

### Сборка для production

```bash
npm run build
```

Собранные файлы будут в папке `build/`

## API Endpoints

Дашборд ожидает следующие endpoints от backend:

- `GET /api/stats/realtime` - Текущее состояние (последние 60 сек)
- `GET /api/stats/count?timeframe={1|5|15}` - Количество уникальных устройств за период
- `GET /api/devices` - Список устройств

### Формат ответа `/api/stats/realtime`

```json
{
  "unique_devices": 42,
  "devices": [
    {
      "mac": "aa:bb:cc:dd:ee:ff",
      "rssi": -65,
      "timestamp": "2024-01-01T12:00:00Z",
      "is_random": false
    }
  ]
}
```

### Формат ответа `/api/stats/count`

```json
{
  "count": 42,
  "active_5min": 15,
  "active_15min": 28
}
```

### Формат ответа `/api/devices`

```json
[
  {
    "mac": "aa:bb:cc:dd:ee:ff",
    "rssi": -65,
    "last_seen": "2024-01-01T12:00:00Z",
    "is_random": false,
    "count": 5
  }
]
```

## Особенности

- ✅ Real-time обновление данных каждые 5 секунд
- ✅ Enterprise-стиль UI, готовый для B2B продаж
- ✅ Адаптивный дизайн
- ✅ Чистая архитектура (SOLID, KISS)
- ✅ Разделение на components, pages, services
- ✅ Маскирование MAC адресов для приватности
- ✅ Визуализация RSSI с цветовой индикацией

## Технологии

- React 18
- Axios для HTTP запросов
- Recharts для графиков
- CSS3 для стилизации

## White-label готовность

Все тексты и стили легко настраиваются для white-label использования. Компоненты не содержат жестко закодированных брендов.
