# Скрипт диагностики проблем запуска сервера
# Проверяет все необходимые компоненты и помогает исправить проблемы

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Диагностика сервера Wi-Fi мониторинга" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()

# 1. Проверка Python
Write-Host "1. Проверка Python..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Python найден: $pythonCheck" -ForegroundColor Green
} else {
    $errors += "Python не найден! Установите Python 3.7 или выше"
    Write-Host "   [ERROR] Python не найден!" -ForegroundColor Red
}

# 2. Проверка зависимостей
Write-Host "2. Проверка зависимостей..." -ForegroundColor Yellow
$requiredPackages = @("flask", "paho-mqtt", "flask-cors")
foreach ($package in $requiredPackages) {
    $result = python -m pip show $package 2>&1 | Out-String
    if ($result -match "Version:") {
        $version = ($result | Select-String -Pattern "Version:\s+(\S+)").Matches.Groups[1].Value
        Write-Host "   [OK] $package версия $version" -ForegroundColor Green
    } else {
        $errors += "Пакет $package не установлен"
        Write-Host "   [ERROR] $package не установлен" -ForegroundColor Red
    }
}

# 3. Проверка порта 5000
Write-Host "3. Проверка порта 5000..." -ForegroundColor Yellow
$port5000 = netstat -ano | Select-String ":5000" | Select-String "LISTENING"
if ($port5000) {
    $pids = @()
    foreach ($line in $port5000) {
        $parts = $line.ToString().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
        $pid = $parts[-1]
        if ($pid -match "^\d+$") {
            $pids += $pid
        }
    }
    $uniquePids = $pids | Sort-Object -Unique
    $warnings += "Порт 5000 занят процессами: $($uniquePids -join ', ')"
    Write-Host "   [WARNING] Порт 5000 занят процессами: $($uniquePids -join ', ')" -ForegroundColor Yellow
    
    Write-Host "   Хотите завершить эти процессы? (Y/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        foreach ($pid in $uniquePids) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "   [OK] Процесс $pid завершен" -ForegroundColor Green
            } catch {
                Write-Host "   [ERROR] Не удалось завершить процесс $pid" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "   [OK] Порт 5000 свободен" -ForegroundColor Green
}

# 4. Проверка MQTT брокера
Write-Host "4. Проверка MQTT брокера (порт 1883)..." -ForegroundColor Yellow
try {
    $mqttAvailable = Test-NetConnection -ComputerName localhost -Port 1883 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($mqttAvailable) {
        Write-Host "   [OK] MQTT брокер доступен на localhost:1883" -ForegroundColor Green
    } else {
        $errors += "MQTT брокер недоступен на localhost:1883. Убедитесь, что Mosquitto запущен."
        Write-Host "   [ERROR] MQTT брокер недоступен" -ForegroundColor Red
        Write-Host "   Подсказка: Запустите Mosquitto или используйте Docker:" -ForegroundColor Yellow
        Write-Host "     docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto" -ForegroundColor Cyan
    }
} catch {
    $errors += "Не удалось проверить MQTT брокер"
    Write-Host "   [ERROR] Не удалось проверить MQTT брокер" -ForegroundColor Red
}

# 5. Проверка файлов проекта
Write-Host "5. Проверка файлов проекта..." -ForegroundColor Yellow
$requiredFiles = @("main.py", "dashboard_api.py", "mqtt_consumer.py", "storage.py", "config.py")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   [OK] $file найден" -ForegroundColor Green
    } else {
        $errors += "Файл $file не найден"
        Write-Host "   [ERROR] $file не найден" -ForegroundColor Red
    }
}

# Итоги
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Результаты диагностики" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[OK] Все проверки пройдены успешно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Запуск сервера:" -ForegroundColor Cyan
    Write-Host "  python main.py" -ForegroundColor White
    Write-Host "  или" -ForegroundColor Cyan
    Write-Host "  .\start_server.ps1" -ForegroundColor White
} else {
    if ($errors.Count -gt 0) {
        Write-Host "[ERROR] Найдены критические ошибки:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "  - $error" -ForegroundColor Red
        }
    }
    if ($warnings.Count -gt 0) {
        Write-Host "[WARNING] Предупреждения:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  - $warning" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
