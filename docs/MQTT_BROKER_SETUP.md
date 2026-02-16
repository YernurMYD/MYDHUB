# Настройка MQTT брокера (Mosquitto)

## Зачем нужен MQTT брокер

Python-сервер (`main.py`) подключается к MQTT брокеру как **клиент**. Отдельно нужен **брокер** (Mosquitto), который принимает сообщения от scanner на роутере и доставляет их consumer'у.

## Установка

### Вариант 1: Mosquitto на Windows (рекомендуется)

**Шаг 1: Установка**

```powershell
# Через Chocolatey
choco install mosquitto

# Или скачайте с https://mosquitto.org/download/
```

**Шаг 2: Конфигурация**

Файл: `C:\Program Files\mosquitto\mosquitto.conf`

```
# Слушать на всех интерфейсах (обязательно для внешних подключений!)
listener 1883 0.0.0.0

# Разрешить анонимные подключения
allow_anonymous true
```

**Шаг 3: Запуск**

```powershell
# Как служба Windows
Start-Service mosquitto
Get-Service mosquitto

# Или вручную
cd "C:\Program Files\mosquitto"
.\mosquitto.exe -c mosquitto.conf
```

### Вариант 2: Docker

```powershell
docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto
```

## Проверка

### 1. Порт слушает на 0.0.0.0

```powershell
netstat -ano | findstr ":1883"
```

**Правильно:**
```
TCP    0.0.0.0:1883           0.0.0.0:0              LISTENING
```

**Неправильно** (только localhost):
```
TCP    127.0.0.1:1883         0.0.0.0:0              LISTENING
```

### 2. Подключение работает

```powershell
Test-NetConnection -ComputerName localhost -Port 1883
```

### 3. Тест с роутера

```bash
# На роутере
mosquitto_pub -h <IP_Windows_PC> -t test -m "test"
```

Если команда выполняется без ошибок -- брокер работает.

## Настройка Firewall

```powershell
# Через скрипт (от имени администратора)
.\setup_firewall.ps1

# Или вручную
New-NetFirewallRule -DisplayName "MQTT Broker" -Direction Inbound -LocalPort 1883 -Protocol TCP -Action Allow
```

## Проверка всей цепочки

```powershell
# 1. Брокер слушает
netstat -ano | findstr ":1883"

# 2. Python сервер подключен
python main.py
# Должно показать: "Подключено к MQTT брокеру localhost:1883"

# 3. Scanner подключается с роутера
# На роутере:
mosquitto_pub -h <IP_PC> -t test -m "test"
```

## Перезапуск Mosquitto

```powershell
Restart-Service mosquitto
```

## Безопасность (для production)

```
# mosquitto.conf
listener 1883 0.0.0.0
allow_anonymous false
password_file C:\Program Files\mosquitto\pwfile
```

Создание файла паролей:
```powershell
cd "C:\Program Files\mosquitto"
.\mosquitto_passwd -c pwfile username
```
