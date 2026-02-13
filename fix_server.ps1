# Simple server diagnostic and fix script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server Diagnostic Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
$pythonVer = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Python: $pythonVer" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Python not found!" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "2. Checking dependencies..." -ForegroundColor Yellow
$packages = @("flask", "paho-mqtt", "flask-cors")
foreach ($pkg in $packages) {
    $check = python -m pip show $pkg 2>&1 | Out-String
    if ($check -match "Version:") {
        Write-Host "   [OK] $pkg installed" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] $pkg not installed" -ForegroundColor Red
        Write-Host "   Installing $pkg..." -ForegroundColor Yellow
        python -m pip install $pkg
    }
}

# Check port 5000
Write-Host "3. Checking port 5000..." -ForegroundColor Yellow
$portCheck = netstat -ano | Select-String ":5000" | Select-String "LISTENING"
if ($portCheck) {
    Write-Host "   [WARNING] Port 5000 is in use" -ForegroundColor Yellow
    $pids = @()
    foreach ($line in $portCheck) {
        $parts = $line.ToString().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
        $pid = $parts[-1]
        if ($pid -match "^\d+$") {
            $pids += $pid
        }
    }
    $uniquePids = $pids | Sort-Object -Unique
    Write-Host "   Processes using port 5000: $($uniquePids -join ', ')" -ForegroundColor Yellow
    Write-Host "   Kill these processes? (Y/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        foreach ($pid in $uniquePids) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "   [OK] Process $pid stopped" -ForegroundColor Green
            } catch {
                Write-Host "   [ERROR] Could not stop process $pid" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "   [OK] Port 5000 is free" -ForegroundColor Green
}

# Check MQTT broker
Write-Host "4. Checking MQTT broker (port 1883)..." -ForegroundColor Yellow
try {
    $mqttCheck = Test-NetConnection -ComputerName localhost -Port 1883 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($mqttCheck) {
        Write-Host "   [OK] MQTT broker is available" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING] MQTT broker not available" -ForegroundColor Yellow
        Write-Host "   Start Mosquitto or use Docker:" -ForegroundColor Yellow
        Write-Host "   docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   [WARNING] Could not check MQTT broker" -ForegroundColor Yellow
}

# Check files
Write-Host "5. Checking project files..." -ForegroundColor Yellow
$files = @("main.py", "dashboard_api.py", "mqtt_consumer.py", "storage.py", "config.py")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   [OK] $file found" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] $file not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnostic complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor White
Write-Host "  or" -ForegroundColor Cyan
Write-Host "  .\start_server.ps1" -ForegroundColor White
Write-Host ""
