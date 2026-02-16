# Устранение проблем

Руководство по диагностике и решению проблем системы MYDhub.

---

## 1. Данные не приходят с роутера

### Диагностика

**На Windows PC:**
```powershell
# 1. Проверка MQTT брокера
Test-NetConnection -ComputerName localhost -Port 1883
netstat -ano | findstr ":1883"
# Должно быть: TCP  0.0.0.0:1883  LISTENING

# 2. Подписка на топик
mosquitto_sub -h localhost -t wifi/probes -v
```

**На роутере:**
```bash
# 1. Проверка конфигурации
cat /etc/scanner.conf

# 2. Сетевая доступность
ping <IP_Windows_PC>

# 3. Тест MQTT
mosquitto_pub -h <IP_Windows_PC> -t test -m "test"

# 4. Статус scanner
/etc/init.d/scanner status
logread | grep scanner | tail -20
```

### Решения

| Проблема | Решение |
|----------|---------|
| MQTT брокер не слушает | Запустите Mosquitto: `Start-Service mosquitto` |
| Слушает только на 127.0.0.1 | Настройте `listener 1883 0.0.0.0` в mosquitto.conf |
| Firewall блокирует | `.\setup_firewall.ps1` (от имени администратора) |
| Неправильный IP в конфиге | Исправьте `MQTT_HOST` в `/etc/scanner.conf` |
| Scanner не запущен | `/etc/init.d/scanner restart` |

---

## 2. Connection refused (MQTT)

### Причины (в порядке вероятности)

1. **Firewall блокирует порт 1883** (90% случаев)
   ```powershell
   .\setup_firewall.ps1
   ```

2. **Mosquitto не настроен на внешние подключения**
   Проверьте `mosquitto.conf`:
   ```
   listener 1883 0.0.0.0
   allow_anonymous true
   ```

3. **Неправильный MQTT_HOST в scanner.conf**
   ```bash
   cat /etc/scanner.conf | grep MQTT_HOST
   # Должно быть IP вашего Windows PC, НЕ роутера!
   ```

4. **MQTT брокер не запущен**
   ```powershell
   netstat -ano | findstr ":1883"
   ```

### Быстрая проверка с роутера

```bash
# Ping
ping <IP_Windows_PC>

# MQTT тест
mosquitto_pub -h <IP_Windows_PC> -t test -m "test"

# Если OK -- перезапуск scanner
/etc/init.d/scanner restart
```

---

## 3. MQTT publish failed / Host unreachable

После channel hopping сеть может не успевать восстановиться.

### Решения

1. Увеличить `NETWORK_SETTLE_TIME` в `/etc/scanner.conf` (попробовать 20--30)
2. Указать `HOME_CHANNEL` явно:
   ```bash
   iw dev wlan0 info | grep channel
   # Вписать результат в HOME_CHANNEL
   ```
3. Увеличить `HOST_WAIT_TIMEOUT` (до 180)
4. Проверить буфер:
   ```bash
   ls /tmp/scanner_buffer/
   ```
   Если файлы есть -- данные сохранены и будут досланы при следующем цикле.

---

## 4. Scanner не запускается / падает

### Диагностика

```bash
# Проверка прав
ls -la /usr/bin/scanner.sh /etc/init.d/scanner

# Проверка зависимостей
which mosquitto_pub tcpdump awk

# Проверка конфигурации
cat /etc/scanner.conf

# Проверка интерфейса
iw dev | grep mon0
ifconfig mon0

# Ручной запуск (видны все ошибки)
/etc/init.d/scanner stop
/usr/bin/scanner.sh
```

### Решения

| Проблема | Решение |
|----------|---------|
| `Permission denied` | `chmod +x /usr/bin/scanner.sh /etc/init.d/scanner` |
| `No such file or directory.common` | CRLF: `sed -i 's/\r$//' /usr/bin/scanner.sh /etc/scanner.conf /etc/init.d/scanner` |
| `Missing required config` | Создать `/etc/scanner.conf` (см. `router/scanner.conf.example`) |
| Нет mosquitto_pub | `opkg install mosquitto-client` |
| Нет tcpdump | `opkg install tcpdump` |
| mon0 не существует | `iw phy phy0 interface add mon0 type monitor && ifconfig mon0 up` |

---

## 5. Интерфейс mon0 не работает

### Создание monitor интерфейса

```bash
# Удалить если существует с ошибками
ifconfig mon0 down 2>/dev/null
iw dev mon0 del 2>/dev/null

# Создать заново
iw phy phy0 interface add mon0 type monitor
ifconfig mon0 up

# Проверка
iw dev mon0 info
```

### Проверка поддержки monitor mode

```bash
iw phy phy0 info | grep monitor
```

Если нет поддержки -- chipset роутера не поддерживает monitor mode.

---

## 6. Нет устройств (c=0)

Scanner работает, но не находит устройства.

### Причины

- Нет Wi-Fi устройств поблизости
- Устройства подключены к сети (не ищут новые)
- Неправильный канал

### Решения

1. Включите Wi-Fi на телефоне, но не подключайтесь к сети
2. Проверьте захват пакетов:
   ```bash
   timeout 30 tcpdump -i mon0 -e -n -s 256 -c 10 "type mgt subtype probe-req"
   ```
3. Проверьте каналы:
   ```bash
   iw dev mon0 info
   ```

---

## 7. API не отвечает

### Диагностика

```powershell
# Проверка порта
netstat -an | findstr 5000

# Проверка здоровья
curl http://localhost:5000/api/health
```

### Решения

| Проблема | Решение |
|----------|---------|
| Сервер не запущен | `python main.py` |
| Порт занят | Измените `API_PORT` в env или config.py |
| Ошибка импорта | `pip install -r requirements.txt` |

---

## 8. График пустой (фронтенд)

### Причины

- Сервер не получил данных (нет MQTT-сообщений)
- Scanner ещё не отправил первый батч (подождите CYCLE_TIME)

### Решения

1. Проверьте API:
   ```powershell
   curl "http://localhost:5000/api/stats/devices_timeseries?timeframe=1h"
   ```
2. Проверьте сводку:
   ```powershell
   curl http://localhost:5000/api/stats/summary
   ```
3. Отправьте тестовые данные:
   ```powershell
   python smoke_check.py
   ```

---

## 9. SCP не работает (sftp-server not found)

На роутере нет SFTP-сервера.

### Решения

**Способ 1: SCP с флагом -O (legacy)**
```powershell
scp -O scanner.sh root@192.168.1.100:/usr/bin/scanner.sh
```

**Способ 2: Через SSH pipe**
```powershell
Get-Content scanner.sh -Raw | ssh root@192.168.1.100 "cat > /usr/bin/scanner.sh"
```

**Способ 3: Вручную через vi**
```bash
ssh root@192.168.1.100
vi /usr/bin/scanner.sh
# Вставить содержимое, сохранить :wq
```

**Способ 4: Установить SFTP**
```bash
opkg install openssh-sftp-server
```

---

## 10. Быстрая диагностика

### На Windows PC

```powershell
# MQTT брокер
netstat -ano | findstr ":1883"

# Firewall
Get-NetFirewallRule -DisplayName "*MQTT*"

# API
curl http://localhost:5000/api/health

# Подписка на MQTT
mosquitto_sub -h localhost -t wifi/probes -v
```

### На роутере

```bash
# Конфигурация
cat /etc/scanner.conf

# MQTT тест
mosquitto_pub -h <IP_PC> -t test -m "test"

# Scanner статус
/etc/init.d/scanner status
logread | grep scanner | tail -20

# Интерфейс
iw dev | grep mon0

# Захват пакетов
timeout 10 tcpdump -i mon0 -e -n -s 256 -c 5 "type mgt subtype probe-req"
```

### Автоматическая диагностика

```powershell
# На Windows PC
python check_system.py
.\diagnose_server.ps1

# На роутере
sh /tmp/diagnose_mqtt.sh
```
