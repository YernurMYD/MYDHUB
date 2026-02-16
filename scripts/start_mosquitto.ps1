# Скрипт для запуска Mosquitto MQTT брокера
# Проверяет установку и запускает брокер

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mosquitto MQTT Broker Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка установки Mosquitto
$mosquittoInstalled = $false
$mosquittoPath = $null

# Проверка службы Windows
Write-Host "1. Checking Mosquitto service..." -ForegroundColor Yellow
$service = Get-Service -Name "*mosquitto*" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "   [OK] Mosquitto service found: $($service.Name)" -ForegroundColor Green
    $mosquittoInstalled = $true
    
    # Проверка статуса службы
    if ($service.Status -eq "Running") {
        Write-Host "   [OK] Service is already running" -ForegroundColor Green
        Write-Host ""
        Write-Host "Mosquitto broker is running!" -ForegroundColor Green
        Write-Host "Check port: netstat -ano | findstr ':1883'" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "   [INFO] Service status: $($service.Status)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [INFO] Mosquitto service not found" -ForegroundColor Yellow
}

# Проверка исполняемого файла
Write-Host ""
Write-Host "2. Checking Mosquitto executable..." -ForegroundColor Yellow
$possiblePaths = @(
    "C:\Program Files\mosquitto\mosquitto.exe",
    "C:\Program Files (x86)\mosquitto\mosquitto.exe",
    "$env:ProgramFiles\mosquitto\mosquitto.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        Write-Host "   [OK] Found: $path" -ForegroundColor Green
        $mosquittoPath = $path
        $mosquittoInstalled = $true
        break
    }
}

if (-not $mosquittoInstalled) {
    Write-Host "   [ERROR] Mosquitto not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Download and install from:" -ForegroundColor Cyan
    Write-Host "  https://mosquitto.org/download/" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Use Chocolatey (if installed):" -ForegroundColor Cyan
    Write-Host "  choco install mosquitto" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Use Docker (if installed):" -ForegroundColor Cyan
    Write-Host "  docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Запуск Mosquitto
Write-Host ""
Write-Host "3. Starting Mosquitto..." -ForegroundColor Yellow

# Попытка запуска службы
if ($service) {
    try {
        Start-Service -Name $service.Name -ErrorAction Stop
        Write-Host "   [OK] Service started successfully" -ForegroundColor Green
        
        # Ожидание запуска
        Start-Sleep -Seconds 2
        
        # Проверка статуса
        $service = Get-Service -Name $service.Name
        if ($service.Status -eq "Running") {
            Write-Host "   [OK] Service is running" -ForegroundColor Green
        } else {
            Write-Host "   [WARNING] Service status: $($service.Status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   [ERROR] Failed to start service: $_" -ForegroundColor Red
        Write-Host "   Trying to run manually..." -ForegroundColor Yellow
        
        # Попытка запуска вручную
        if ($mosquittoPath) {
            $configPath = Join-Path (Split-Path $mosquittoPath) "mosquitto.conf"
            if (Test-Path $configPath) {
                Write-Host "   Starting: $mosquittoPath -c $configPath" -ForegroundColor Cyan
                Start-Process -FilePath $mosquittoPath -ArgumentList "-c", $configPath -WindowStyle Hidden
            } else {
                Write-Host "   Starting: $mosquittoPath" -ForegroundColor Cyan
                Start-Process -FilePath $mosquittoPath -WindowStyle Hidden
            }
        }
    }
} else {
    # Запуск вручную, если службы нет
    if ($mosquittoPath) {
        Write-Host "   Starting Mosquitto manually..." -ForegroundColor Yellow
        $configPath = Join-Path (Split-Path $mosquittoPath) "mosquitto.conf"
        
        if (Test-Path $configPath) {
            Write-Host "   Command: $mosquittoPath -c $configPath" -ForegroundColor Cyan
            Start-Process -FilePath $mosquittoPath -ArgumentList "-c", $configPath -WindowStyle Hidden
        } else {
            Write-Host "   Command: $mosquittoPath" -ForegroundColor Cyan
            Start-Process -FilePath $mosquittoPath -WindowStyle Hidden
        }
        
        Write-Host "   [OK] Mosquitto started (running in background)" -ForegroundColor Green
    }
}

# Проверка порта
Write-Host ""
Write-Host "4. Checking port 1883..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$portCheck = netstat -ano | findstr ":1883" | findstr "LISTENING"
if ($portCheck) {
    Write-Host "   [OK] Port 1883 is listening" -ForegroundColor Green
    Write-Host "   $portCheck" -ForegroundColor Cyan
} else {
    Write-Host "   [WARNING] Port 1883 is not listening yet" -ForegroundColor Yellow
    Write-Host "   Wait a few seconds and check again: netstat -ano | findstr ':1883'" -ForegroundColor Cyan
}

# Проверка конфигурации
Write-Host ""
Write-Host "5. Checking configuration..." -ForegroundColor Yellow
if ($mosquittoPath) {
    $configPath = Join-Path (Split-Path $mosquittoPath) "mosquitto.conf"
    if (Test-Path $configPath) {
        Write-Host "   [OK] Config file found: $configPath" -ForegroundColor Green
        
        # Проверка настройки listener
        $configContent = Get-Content $configPath -Raw
        if ($configContent -match "listener\s+1883") {
            Write-Host "   [OK] Listener configured for port 1883" -ForegroundColor Green
        } else {
            Write-Host "   [WARNING] Listener not found in config" -ForegroundColor Yellow
            Write-Host "   Add this line to $configPath :" -ForegroundColor Cyan
            Write-Host "   listener 1883 0.0.0.0" -ForegroundColor White
            Write-Host "   allow_anonymous true" -ForegroundColor White
        }
    } else {
        Write-Host "   [WARNING] Config file not found" -ForegroundColor Yellow
        Write-Host "   Create $configPath with:" -ForegroundColor Cyan
        Write-Host "   listener 1883 0.0.0.0" -ForegroundColor White
        Write-Host "   allow_anonymous true" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify broker is running: netstat -ano | findstr ':1883'" -ForegroundColor White
Write-Host "2. Test from router: mosquitto_pub -h 192.168.1.101 -t test -m 'test'" -ForegroundColor White
Write-Host "3. Restart scanner: ssh root@192.168.1.100 '/etc/init.d/scanner restart'" -ForegroundColor White
Write-Host ""
