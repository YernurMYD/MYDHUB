# Архитектура дашборда для продажи доступа к данным Wi-Fi мониторинга

## 1. Роли и права доступа

### 1.1 Иерархия ролей

```
┌─────────────────┐
│   Super Admin   │  Полный доступ ко всем функциям
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│ Admin │ │ Manager │  Управление пользователями и данными
└───┬───┘ └───┬─────┘
    │         │
    │    ┌────┴────┐
    │    │         │
┌───▼────▼──┐ ┌───▼──────┐
│  Viewer   │ │  Client  │  Просмотр данных с ограничениями
└───────────┘ └──────────┘
```

### 1.2 Детальное описание ролей

#### **Super Admin**
- Полный доступ ко всем функциям системы
- Управление всеми пользователями и ролями
- Доступ к системным настройкам и логам
- Управление подписками и тарифами
- Экспорт всех данных без ограничений

#### **Admin**
- Управление пользователями (создание, редактирование, удаление)
- Управление подписками и тарифами
- Доступ ко всем данным без ограничений
- Просмотр статистики использования API
- Управление edge-устройствами

#### **Manager**
- Просмотр всех данных
- Управление клиентами (Client роль)
- Создание и управление API ключами для клиентов
- Просмотр аналитики и отчетов
- Ограниченный доступ к системным настройкам

#### **Viewer**
- Просмотр данных в реальном времени
- Доступ к статистике и аналитике
- Экспорт данных в ограниченном объеме
- Нет доступа к управлению пользователями

#### **Client** (API клиент)
- Доступ только через API с API ключом
- Ограниченный доступ к данным согласно подписке
- Rate limiting согласно тарифу
- Нет доступа к веб-интерфейсу

### 1.3 Матрица прав доступа

| Функция | Super Admin | Admin | Manager | Viewer | Client |
|---------|-------------|-------|---------|--------|--------|
| Просмотр всех данных | ✅ | ✅ | ✅ | ✅ | ⚠️* |
| Управление пользователями | ✅ | ✅ | ❌ | ❌ | ❌ |
| Управление подписками | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| Создание API ключей | ✅ | ✅ | ✅ | ❌ | ❌ |
| Экспорт данных | ✅ | ✅ | ✅ | ⚠️ | ⚠️* |
| Системные настройки | ✅ | ❌ | ❌ | ❌ | ❌ |
| Просмотр логов | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Управление edge-устройствами | ✅ | ✅ | ❌ | ❌ | ❌ |

⚠️ - Ограниченный доступ  
⚠️* - Согласно тарифу подписки

---

## 2. API Архитектура

### 2.1 Структура API

```
/api
├── /v1                    # Версионирование API
│   ├── /auth              # Аутентификация
│   │   ├── POST /login
│   │   ├── POST /refresh
│   │   └── POST /logout
│   │
│   ├── /users             # Управление пользователями (Admin+)
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── GET /{id}
│   │   ├── PUT /{id}
│   │   └── DELETE /{id}
│   │
│   ├── /devices           # Данные устройств
│   │   ├── GET /          # Список устройств
│   │   ├── GET /{mac}     # Информация об устройстве
│   │   ├── GET /stats     # Статистика устройств
│   │   └── GET /export    # Экспорт данных
│   │
│   ├── /data              # Временные данные
│   │   ├── GET /recent    # Последние данные
│   │   ├── GET /range     # Данные за период
│   │   └── GET /stream    # WebSocket stream
│   │
│   ├── /dashboard         # Данные для дашборда
│   │   ├── GET /overview  # Обзор
│   │   ├── GET /analytics # Аналитика
│   │   └── GET /realtime  # Данные реального времени
│   │
│   ├── /subscriptions     # Подписки (Admin+)
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── PUT /{id}
│   │   └── DELETE /{id}
│   │
│   ├── /api-keys          # API ключи
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── PUT /{id}
│   │   └── DELETE /{id}
│   │
│   └── /edge-devices      # Edge устройства (Admin+)
│       ├── GET /
│       ├── POST /
│       ├── PUT /{id}
│       └── DELETE /{id}
```

### 2.2 Аутентификация и авторизация

#### **JWT Token Based Authentication**
```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │────────▶│   API    │────────▶│   Auth   │
│          │         │ Gateway  │         │ Service  │
└──────────┘         └──────────┘         └──────────┘
     │                     │                     │
     │ 1. Login Request    │                     │
     │─────────────────────▶│                     │
     │                     │ 2. Validate        │
     │                     │────────────────────▶│
     │                     │ 3. JWT Token       │
     │                     │◀────────────────────│
     │ 4. JWT Token        │                     │
     │◀────────────────────│                     │
     │                     │                     │
     │ 5. API Request + JWT│                     │
     │─────────────────────▶│                     │
     │                     │ 6. Validate Token  │
     │                     │────────────────────▶│
     │                     │ 7. User + Roles    │
     │                     │◀────────────────────│
     │ 8. Response         │                     │
     │◀────────────────────│                     │
```

#### **API Key Authentication** (для Client роли)
```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │────────▶│   API    │────────▶│   DB     │
│  (API)   │         │ Gateway  │         │          │
└──────────┘         └──────────┘         └──────────┘
     │                     │                     │
     │ 1. Request + API Key│                     │
     │─────────────────────▶│                     │
     │                     │ 2. Validate Key    │
     │                     │────────────────────▶│
     │                     │ 3. Subscription    │
     │                     │    + Rate Limits   │
     │                     │◀────────────────────│
     │ 4. Response         │                     │
     │◀────────────────────│                     │
```

### 2.3 Rate Limiting по ролям

| Роль | Requests/min | Requests/hour | Requests/day |
|------|--------------|---------------|--------------|
| Super Admin | Unlimited | Unlimited | Unlimited |
| Admin | 1000 | 50000 | 1000000 |
| Manager | 500 | 25000 | 500000 |
| Viewer | 100 | 5000 | 100000 |
| Client (Basic) | 60 | 3000 | 50000 |
| Client (Pro) | 300 | 15000 | 300000 |
| Client (Enterprise) | 1000 | 50000 | 1000000 |

### 2.4 Квоты данных по подпискам

| Подписка | Макс. запросов/день | Исторические данные | Экспорт | WebSocket |
|----------|---------------------|---------------------|---------|-----------|
| Basic | 10,000 | 7 дней | ❌ | ❌ |
| Pro | 100,000 | 30 дней | ✅ (CSV) | ✅ |
| Enterprise | Unlimited | Unlimited | ✅ (CSV, JSON) | ✅ |

---

## 3. Масштабирование

### 3.1 Горизонтальное масштабирование

```
                    ┌─────────────┐
                    │   Load      │
                    │  Balancer   │
                    │  (Nginx)    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │ API     │        │ API     │        │ API     │
   │ Server  │        │ Server  │        │ Server  │
   │ (Node 1)│        │ (Node 2)│        │ (Node 3)│
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Redis     │
                    │  (Cache +   │
                    │   Sessions) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │   (Main DB) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  TimescaleDB│
                    │ (Time-series│
                    │    Data)    │
                    └─────────────┘
```

### 3.2 Вертикальное масштабирование

#### **Текущая архитектура (MVP)**
```
┌─────────────────┐
│  Single Server  │
│  - MQTT Consumer│
│  - API Server   │
│  - In-Memory DB │
└─────────────────┘
```

#### **Рекомендуемая архитектура (Production)**

**Уровень 1: Разделение сервисов**
```
┌─────────────────┐     ┌─────────────────┐
│  MQTT Consumer  │────▶│  Message Queue  │
│   (Worker)      │     │   (RabbitMQ)    │
└─────────────────┘     └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Data Processor │
                         │    (Worker)     │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  API Server     │
                         │   (Flask/FastAPI)│
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  PostgreSQL +   │
                         │   TimescaleDB   │
                         └─────────────────┘
```

**Уровень 2: Микросервисная архитектура**
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Auth       │    │   Data       │    │   Analytics  │
│   Service    │    │   Service    │    │   Service    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  API Gateway │
                    │  (Kong/Tyk) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Clients   │
                    └─────────────┘
```

### 3.3 Стратегии масштабирования данных

#### **Кэширование**
- **Redis** для кэширования часто запрашиваемых данных
- TTL: 5-60 секунд в зависимости от типа данных
- Кэширование статистики, топ устройств, последних данных

#### **Партиционирование данных**
- По времени: ежедневные/еженедельные партиции
- По edge-устройствам: данные от разных устройств в отдельных партициях
- По MAC адресам: хеш-партиционирование для больших объемов

#### **Архивирование**
- Горячие данные (последние 7 дней) - In-Memory / Redis
- Теплые данные (7-30 дней) - PostgreSQL / TimescaleDB
- Холодные данные (30+ дней) - Object Storage (S3/MinIO)

### 3.4 Масштабирование MQTT

```
Edge Devices
    │
    ├──▶ MQTT Broker 1 (Region 1)
    │         │
    │         └──▶ Consumer Pool 1
    │
    ├──▶ MQTT Broker 2 (Region 2)
    │         │
    │         └──▶ Consumer Pool 2
    │
    └──▶ MQTT Broker 3 (Region 3)
              │
              └──▶ Consumer Pool 3
```

**MQTT Broker кластеризация:**
- Mosquitto с плагином кластеризации
- Или HiveMQ / EMQ X для enterprise решений
- Балансировка нагрузки между брокерами

---

## 4. Безопасность

### 4.1 Многоуровневая защита

```
┌─────────────────────────────────────────┐
│  Layer 1: Network Security              │
│  - Firewall Rules                       │
│  - DDoS Protection (Cloudflare)        │
│  - VPN для административного доступа   │
└─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│  Layer 2: Transport Security            │
│  - HTTPS/TLS 1.3 (API)                  │
│  - MQTT over TLS (MQTTS)                │
│  - Certificate Pinning                  │
└─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│  Layer 3: Authentication                │
│  - JWT Tokens (short-lived)              │
│  - Refresh Tokens (long-lived)          │
│  - API Keys (HMAC signed)                │
│  - 2FA для Admin ролей                  │
└─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│  Layer 4: Authorization                 │
│  - Role-Based Access Control (RBAC)     │
│  - Resource-Level Permissions           │
│  - Attribute-Based Access Control (ABAC)│
└─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│  Layer 5: Data Security                 │
│  - Encryption at Rest                    │
│  - Encryption in Transit                 │
│  - MAC Address Hashing (опционально)    │
│  - Data Anonymization                    │
└─────────────────────────────────────────┘
```

### 4.2 Аутентификация

#### **JWT Token Structure**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "123",
    "role": "viewer",
    "permissions": ["read:devices", "read:stats"],
    "subscription": "pro",
    "exp": 1234567890,
    "iat": 1234567890
  }
}
```

#### **Token Lifecycle**
- **Access Token**: 15 минут (короткоживущий)
- **Refresh Token**: 7 дней (хранится в HttpOnly cookie)
- **API Key**: Без срока действия (можно отозвать)

### 4.3 Авторизация

#### **RBAC Implementation**
```python
# Пример структуры разрешений
PERMISSIONS = {
    "read:devices": ["viewer", "manager", "admin", "super_admin"],
    "write:devices": ["admin", "super_admin"],
    "read:users": ["manager", "admin", "super_admin"],
    "write:users": ["admin", "super_admin"],
    "read:subscriptions": ["manager", "admin", "super_admin"],
    "write:subscriptions": ["admin", "super_admin"],
    "read:logs": ["admin", "super_admin"],
    "write:system": ["super_admin"]
}
```

#### **Resource-Level Permissions**
- Клиенты могут видеть только свои данные (если применимо)
- Ограничение доступа к данным по edge-устройствам
- Временные ограничения доступа (например, только последние 24 часа)

### 4.4 Защита данных

#### **Encryption**
- **At Rest**: AES-256 для базы данных
- **In Transit**: TLS 1.3 для всех соединений
- **Sensitive Fields**: Дополнительное шифрование для MAC адресов (опционально)

#### **MAC Address Privacy**
```python
# Опциональное хеширование MAC адресов
import hashlib
import hmac

def hash_mac(mac: str, salt: str) -> str:
    """Хеширование MAC адреса для приватности"""
    return hmac.new(
        salt.encode(),
        mac.encode(),
        hashlib.sha256
    ).hexdigest()[:12]  # Первые 12 символов
```

### 4.5 Защита от атак

#### **Rate Limiting**
- Per-user rate limiting
- Per-IP rate limiting
- Per-API-key rate limiting
- Adaptive rate limiting (снижение при подозрительной активности)

#### **Input Validation**
- Валидация всех входных данных
- Sanitization для предотвращения инъекций
- Максимальные размеры запросов

#### **Audit Logging**
```python
# Структура логов аудита
{
    "timestamp": "2024-01-01T00:00:00Z",
    "user_id": "123",
    "role": "viewer",
    "action": "read:devices",
    "resource": "/api/v1/devices",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "status": "success",
    "response_time_ms": 45
}
```

### 4.6 Безопасность MQTT

#### **MQTT Security**
- **Authentication**: Username/Password или Client Certificates
- **Authorization**: ACL (Access Control List) для топиков
- **TLS**: Обязательное использование MQTTS
- **Topic Isolation**: Разделение топиков по edge-устройствам

```
Топики:
- wifi/probes/{device_id}  # Изолированные топики
- wifi/status/{device_id}  # Статус устройств
- wifi/commands/{device_id} # Команды (только для авторизованных)
```

---

## 5. Мониторинг и наблюдаемость

### 5.1 Метрики

- **Performance**: Response time, Throughput, Error rate
- **Business**: Active users, API calls, Data volume
- **Infrastructure**: CPU, Memory, Disk, Network

### 5.2 Логирование

- **Application Logs**: Структурированные логи (JSON)
- **Access Logs**: Все API запросы
- **Audit Logs**: Действия пользователей
- **Error Logs**: Ошибки и исключения

### 5.3 Алертинг

- Критические ошибки
- Превышение rate limits
- Недоступность сервисов
- Аномальная активность

---

## 6. Рекомендации по внедрению

### Фаза 1: MVP (Текущая)
- Базовая аутентификация (JWT)
- Простые роли (Admin, Viewer)
- In-Memory хранилище
- Базовый API

### Фаза 2: Production Ready
- Полная система ролей
- PostgreSQL + TimescaleDB
- Redis кэширование
- Rate limiting
- Audit logging

### Фаза 3: Масштабирование
- Горизонтальное масштабирование
- Микросервисная архитектура
- Кластеризация MQTT
- CDN для статики

### Фаза 4: Enterprise
- Multi-tenancy
- Географическое распределение
- Advanced analytics
- Compliance (GDPR, etc.)

---

## 7. Технологический стек (рекомендации)

### Backend
- **API Framework**: FastAPI (лучше производительность) или Flask
- **Database**: PostgreSQL + TimescaleDB для временных рядов
- **Cache**: Redis
- **Message Queue**: RabbitMQ или Apache Kafka
- **MQTT Broker**: Mosquitto (open source) или HiveMQ (enterprise)

### Security
- **Authentication**: PyJWT, python-jose
- **Password Hashing**: bcrypt, argon2
- **Encryption**: cryptography (Fernet)

### Monitoring
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana) или Loki
- **APM**: Sentry для отслеживания ошибок

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (для начала), Kubernetes (для масштабирования)
- **Load Balancer**: Nginx или Traefik

---

## 8. Схема базы данных (основные таблицы)

```sql
-- Пользователи
users (
    id, email, password_hash, role, 
    created_at, updated_at, last_login
)

-- API ключи
api_keys (
    id, user_id, key_hash, name, 
    permissions, rate_limit, expires_at, 
    created_at, last_used
)

-- Подписки
subscriptions (
    id, user_id, plan, status, 
    start_date, end_date, features
)

-- Edge устройства
edge_devices (
    id, name, location, mqtt_topic, 
    status, last_seen, created_at
)

-- Устройства (MAC адреса)
devices (
    mac, first_seen, last_seen, 
    best_rssi, count, edge_device_id
)

-- Временные данные (TimescaleDB)
device_data (
    time, mac, rssi, edge_device_id
) -- Hypertable для временных рядов

-- Аудит логи
audit_logs (
    id, user_id, action, resource, 
    ip_address, timestamp, status
)
```

---

## Заключение

Данная архитектура обеспечивает:
- ✅ Масштабируемость от MVP до Enterprise
- ✅ Безопасность на всех уровнях
- ✅ Гибкую систему ролей и подписок
- ✅ Готовность к коммерческому использованию
- ✅ Простоту внедрения по фазам

Архитектура следует принципам SOLID и KISS, обеспечивая простоту понимания и поддержки на начальных этапах, с возможностью масштабирования при росте нагрузки.
