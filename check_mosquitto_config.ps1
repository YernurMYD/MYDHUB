# Скрипт для проверки и настройки конфигурации Mosquitto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mosquitto Configuration Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$configPath = "C:\Program Files\mosquitto\mosquitto.conf"

# Проверка файла конфигурации
if (Test-Path $configPath) {
    Write-Host "[OK] Config file found: $configPath" -ForegroundColor Green
    Write-Host ""
    
    $configContent = Get-Content $configPath -Raw
    
    # Проверка listener
    Write-Host "Checking listener configuration..." -ForegroundColor Yellow
    if ($configContent -match "listener\s+1883\s+0\.0\.0\.0") {
        Write-Host "  [OK] Listener configured for 0.0.0.0:1883 (accepts external connections)" -ForegroundColor Green
    } elseif ($configContent -match "listener\s+1883") {
        Write-Host "  [WARNING] Listener found but may not accept external connections" -ForegroundColor Yellow
        Write-Host "  Current config: $($configContent -match 'listener\s+1883[^\r\n]*')" -ForegroundColor Cyan
    } else {
        Write-Host "  [ERROR] Listener not configured!" -ForegroundColor Red
        Write-Host "  Adding listener configuration..." -ForegroundColor Yellow
        
        # Добавление конфигурации
        $newConfig = @"

# MQTT Listener - accepts connections from all interfaces
listener 1883 0.0.0.0

# Allow anonymous connections (for testing)
allow_anonymous true

"@
        
        # Проверка прав администратора для записи
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsPrincipal]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if ($isAdmin) {
            Add-Content -Path $configPath -Value $newConfig
            Write-Host "  [OK] Configuration added" -ForegroundColor Green
            Write-Host "  [INFO] Restart Mosquitto service: Restart-Service mosquitto" -ForegroundColor Cyan
        } else {
            Write-Host "  [ERROR] Need Administrator rights to modify config" -ForegroundColor Red
            Write-Host "  Run PowerShell as Administrator and add to $configPath :" -ForegroundColor Yellow
            Write-Host $newConfig -ForegroundColor White
        }
    }
    
    # Проверка allow_anonymous
    Write-Host ""
    Write-Host "Checking authentication..." -ForegroundColor Yellow
    if ($configContent -match "allow_anonymous\s+true") {
        Write-Host "  [OK] Anonymous connections allowed" -ForegroundColor Green
    } elseif ($configContent -match "allow_anonymous\s+false") {
        Write-Host "  [WARNING] Anonymous connections disabled" -ForegroundColor Yellow
        Write-Host "  Scanner may need authentication configured" -ForegroundColor Yellow
    } else {
        Write-Host "  [INFO] allow_anonymous not set (defaults to false)" -ForegroundColor Cyan
    }
    
} else {
    Write-Host "[WARNING] Config file not found: $configPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Create config file with:" -ForegroundColor Cyan
    Write-Host "listener 1883 0.0.0.0" -ForegroundColor White
    Write-Host "allow_anonymous true" -ForegroundColor White
}

# Проверка порта
Write-Host ""
Write-Host "Checking port 1883..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr ":1883" | findstr "LISTENING"
if ($portCheck) {
    Write-Host "  [OK] Port 1883 is listening" -ForegroundColor Green
    foreach ($line in $portCheck) {
        if ($line -match "0\.0\.0\.0:1883") {
            Write-Host "  [OK] Listening on 0.0.0.0:1883 (accepts external connections)" -ForegroundColor Green
        } elseif ($line -match "127\.0\.0\.1:1883") {
            Write-Host "  [ERROR] Only listening on 127.0.0.1:1883 (localhost only!)" -ForegroundColor Red
            Write-Host "  Update config to: listener 1883 0.0.0.0" -ForegroundColor Yellow
        } else {
            Write-Host "  [INFO] $line" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "  [ERROR] Port 1883 is not listening" -ForegroundColor Red
    Write-Host "  Start Mosquitto: Start-Service mosquitto" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Check complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
