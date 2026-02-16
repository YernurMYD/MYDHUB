# Скрипт настройки сервера на Windows
# Запустите в PowerShell от имени администратора

# Переход в корень проекта
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "=== Настройка Wi-Fi мониторинга сервера ===" -ForegroundColor Green

# Проверка Python
Write-Host "`nПроверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: Python не найден! Установите Python 3.7+" -ForegroundColor Red
    exit 1
}

# Установка зависимостей
Write-Host "`nУстановка Python зависимостей..." -ForegroundColor Yellow
if (Test-Path "backend/requirements.txt") {
    pip install -r backend/requirements.txt
    Write-Host "Зависимости установлены" -ForegroundColor Green
} else {
    Write-Host "ОШИБКА: Файл backend/requirements.txt не найден!" -ForegroundColor Red
    exit 1
}

# Проверка MQTT брокера
Write-Host "`nПроверка MQTT брокера..." -ForegroundColor Yellow
$mqttPort = Get-NetTCPConnection -LocalPort 1883 -ErrorAction SilentlyContinue
if ($mqttPort) {
    Write-Host "MQTT брокер уже запущен на порту 1883" -ForegroundColor Green
} else {
    Write-Host "ВНИМАНИЕ: MQTT брокер не найден на порту 1883" -ForegroundColor Yellow
    Write-Host "Установите Mosquitto:" -ForegroundColor Yellow
    Write-Host "  1. Скачайте с https://mosquitto.org/download/" -ForegroundColor Cyan
    Write-Host "  2. Или используйте Docker: docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto" -ForegroundColor Cyan
}

# Создание .env файла (если не существует)
if (-not (Test-Path ".env")) {
    Write-Host "`nСоздание файла .env..." -ForegroundColor Yellow
    @"
# MQTT настройки
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC=wifi/probes
MQTT_CLIENT_ID=wifi_consumer

# API настройки
API_HOST=0.0.0.0
API_PORT=5000
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Файл .env создан с настройками по умолчанию" -ForegroundColor Green
    Write-Host "При необходимости отредактируйте .env для изменения настроек" -ForegroundColor Cyan
} else {
    Write-Host "`nФайл .env уже существует" -ForegroundColor Green
}

# Проверка firewall
Write-Host "`nПроверка правил firewall для порта 1883..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "MQTT Broker" -ErrorAction SilentlyContinue
if (-not $firewallRule) {
    Write-Host "Создание правила firewall для MQTT (порт 1883)..." -ForegroundColor Yellow
    try {
        New-NetFirewallRule -DisplayName "MQTT Broker" -Direction Inbound -LocalPort 1883 -Protocol TCP -Action Allow -ErrorAction Stop
        Write-Host "Правило firewall создано" -ForegroundColor Green
    } catch {
        Write-Host "ВНИМАНИЕ: Не удалось создать правило firewall автоматически" -ForegroundColor Yellow
        Write-Host "Создайте правило вручную: разрешите входящие подключения на порт 1883" -ForegroundColor Cyan
    }
} else {
    Write-Host "Правило firewall уже существует" -ForegroundColor Green
}

Write-Host "`n=== Настройка завершена! ===" -ForegroundColor Green
Write-Host "`nДля запуска сервера выполните:" -ForegroundColor Yellow
Write-Host "  python backend/main.py" -ForegroundColor Cyan
Write-Host "`nИли используйте скрипт:" -ForegroundColor Yellow
Write-Host "  .\scripts\start_server.ps1" -ForegroundColor Cyan
