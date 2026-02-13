# Настройка роутера OpenWrt

Файлы и инструкции для настройки Wi-Fi сканера на роутере OpenWrt.

## Файлы

| Файл | Назначение | Куда копировать |
|------|-----------|-----------------|
| `scanner.conf.example` | Конфигурация сканера | `/etc/scanner.conf` |
| `scanner.init` | Init-скрипт автозапуска (procd) | `/etc/init.d/scanner` |
| `setup_router.sh` | Автоматическая настройка | `/tmp/setup_router.sh` |
| `diagnose_mqtt.sh` | Диагностика MQTT | `/tmp/diagnose_mqtt.sh` |
| `../scanner.sh` | Основной скрипт сканера | `/usr/bin/scanner.sh` |

## Быстрая настройка

### 1. Установите пакеты на роутере

```bash
opkg update
opkg install mosquitto-client tcpdump coreutils-timeout
```

### 2. Скопируйте файлы с ПК

```powershell
# С Windows PC (замените 192.168.1.100 на IP роутера)
scp -O ../scanner.sh root@192.168.1.100:/usr/bin/scanner.sh
scp -O scanner.conf.example root@192.168.1.100:/etc/scanner.conf
scp -O scanner.init root@192.168.1.100:/etc/init.d/scanner
```

### 3. Настройте конфигурацию

```bash
ssh root@192.168.1.100
vi /etc/scanner.conf
```

**Обязательно измените `MQTT_HOST`** на IP вашего Windows PC.

Параметры:

| Параметр | Обязательный | По умолчанию | Описание |
|----------|-------------|-------------|----------|
| `INTERFACE` | да | `mon0` | Monitor интерфейс |
| `MQTT_HOST` | да | -- | IP Windows PC с MQTT брокером |
| `MQTT_TOPIC` | да | `wifi/probes` | MQTT топик |
| `CYCLE_TIME` | нет | `600` | Интервал отправки (сек) |
| `HOME_CHANNEL` | нет | авто | Рабочий канал Wi-Fi |
| `NETWORK_SETTLE_TIME` | нет | `15` | Ожидание после channel hop (сек) |
| `HOST_WAIT_TIMEOUT` | нет | `120` | Макс. ожидание хоста (сек) |
| `MQTT_RETRIES` | нет | `5` | Попытки отправки |
| `MQTT_RETRY_DELAY` | нет | `3` | Начальная задержка (сек) |
| `BUFFER_MAX` | нет | `10` | Макс. буферизованных сообщений |

### 4. Установите права и создайте интерфейс

```bash
chmod +x /usr/bin/scanner.sh
chmod +x /etc/init.d/scanner

iw phy phy0 interface add mon0 type monitor
ifconfig mon0 up
```

### 5. Запустите

```bash
/etc/init.d/scanner enable   # Автозапуск
/etc/init.d/scanner start    # Запуск сейчас
```

## Альтернатива: автоматическая настройка

```bash
scp -O setup_router.sh root@192.168.1.100:/tmp/
ssh root@192.168.1.100 "chmod +x /tmp/setup_router.sh && /tmp/setup_router.sh"
```

## Проверка работы

```bash
# Статус
/etc/init.d/scanner status

# Логи
logread | grep scanner
logread -f | grep scanner

# Процесс
ps | grep scanner

# Тест MQTT
mosquitto_pub -h <IP_PC> -t wifi/probes -m '{"t":1234567890,"d":[{"m":"aa:bb:cc:dd:ee:ff","r":-63,"x":0}],"c":1}'

# Тест захвата пакетов
timeout 30 tcpdump -i mon0 -e -n -s 256 -c 10 "type mgt subtype probe-req"
```

## Как работает scanner.sh

1. Проверяет/создаёт monitor интерфейс
2. Определяет рабочий канал Wi-Fi (HOME_CHANNEL)
3. В бесконечном цикле:
   - Перехватывает Probe Request на каналах 1, 6, 11 (channel hopping)
   - Восстанавливает сеть (возвращает канал + ожидание NETWORK_SETTLE_TIME)
   - Парсит tcpdump-вывод через awk (извлекает MAC, RSSI, randomized flag)
   - Агрегирует данные с дедупликацией по MAC (лучший RSSI)
   - Формирует JSON: `{"t":unix_ts,"d":[{"m":"mac","r":rssi,"x":0/1}],"c":N}`
   - Ожидает доступности MQTT хоста
   - Досылает буферизованные данные (если были)
   - Отправляет текущий батч в MQTT
   - При ошибке -- сохраняет в локальный буфер `/tmp/scanner_buffer/`

## Обновление scanner.sh

Если роутер уже настроен и нужно обновить только скрипт:

```powershell
scp -O ../scanner.sh root@192.168.1.100:/usr/bin/scanner.sh
ssh root@192.168.1.100 "/etc/init.d/scanner restart"
```

## CRLF проблемы

Если файлы скопированы с Windows и содержат CRLF:

```bash
sed -i 's/\r$//' /usr/bin/scanner.sh /etc/scanner.conf /etc/init.d/scanner
```
