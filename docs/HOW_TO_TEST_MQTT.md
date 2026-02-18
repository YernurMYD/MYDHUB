# Как проверить MQTT

## Способ 1: mosquitto_sub (рекомендуется)

### Шаг 1: Подписка на топик

```powershell
# Тестовый топик
mosquitto_sub -h localhost -t test -v

# Или топик scanner
mosquitto_sub -h localhost -t wifi/probes -v
```

### Шаг 2: Отправка сообщения

В другом терминале:

```powershell
# С Windows PC
mosquitto_pub -h localhost -t test -m "test message"

# Или с роутера
mosquitto_pub -h <IP_Windows_PC> -t test -m "test from router"
```

### Шаг 3: Сообщение появится в первом окне

## Способ 2: Python-скрипт

```powershell
python tests/test_mqtt_receive.py
```

Затем отправьте сообщение с роутера или из другого терминала.

## Способ 3: Через основной сервер

Если `backend/main.py` запущен, он автоматически получает сообщения из `wifi/probes`.

```powershell
# Проверка через API
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/devices
```

## Тест топика wifi/probes

### На Windows PC (подписка):

```powershell
mosquitto_sub -h localhost -t wifi/probes -v
```

### С роутера (отправка тестового сообщения):

```bash
mosquitto_pub -h <IP_PC> -t wifi/probes -m '{"t":1234567890,"d":[{"m":"aa:bb:cc:dd:ee:ff","r":-63,"x":0}],"c":1}'
```

JSON должен появиться в окне mosquitto_sub.

## Тест через smoke_check.py

```powershell
# Запустите сервер в одном терминале
python backend/main.py

# В другом терминале
python tests/smoke_check.py
```

Скрипт опубликует тестовые данные в оба формата и проверит API.

## Если mosquitto_sub не найден

```powershell
# Установите Mosquitto
choco install mosquitto

# Или используйте Python-скрипт
python tests/test_mqtt_receive.py
```

## Если сообщения не приходят

1. **MQTT брокер запущен?**
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 1883
   ```

2. **Firewall настроен?**
   ```powershell
   .\scripts\setup_firewall.ps1
   ```

3. **Правильный IP в конфиге роутера?**
   ```bash
   cat /etc/scanner.conf | grep MQTT_HOST
   ```

Подробнее: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
