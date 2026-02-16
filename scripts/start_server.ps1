# Скрипт запуска сервера Wi-Fi мониторинга на Windows
# Запустите этот файл в PowerShell для старта MQTT Consumer и API

# Переход в корень проекта
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "========================================" -ForegroundColor Green
Write-Host "Запуск сервера Wi-Fi мониторинга" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Проверка Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: Python не найден!" -ForegroundColor Red
    Write-Host "Установите Python 3.7 или выше" -ForegroundColor Yellow
    exit 1
}

# Проверка зависимостей
Write-Host "Проверка зависимостей..." -ForegroundColor Yellow
python -m pip show paho-mqtt > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Установка зависимостей..." -ForegroundColor Yellow
    python -m pip install -r backend/requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ОШИБКА: Не удалось установить зависимости" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Запуск сервера..." -ForegroundColor Green
Write-Host ""
Write-Host "Сервер будет доступен на:" -ForegroundColor Cyan
Write-Host "  - API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "  - MQTT: localhost:1883" -ForegroundColor Cyan
Write-Host ""
Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""

python backend/main.py
