# Скрипт настройки Windows Firewall для MQTT брокера
# Требует запуска от имени администратора

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MQTT Firewall Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Cyan
    Write-Host "1. Right-click PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "3. Navigate to project directory" -ForegroundColor White
    Write-Host "4. Run: .\setup_firewall.ps1" -ForegroundColor White
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Проверка существующего правила
Write-Host "Checking existing firewall rules..." -ForegroundColor Yellow
$existingRule = Get-NetFirewallRule -DisplayName "MQTT Broker" -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "[INFO] Firewall rule already exists" -ForegroundColor Cyan
    $existingRule | Format-Table DisplayName, Enabled, Direction, Action
    Write-Host ""
    Write-Host "Do you want to recreate it? (Y/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Remove-NetFirewallRule -DisplayName "MQTT Broker" -ErrorAction SilentlyContinue
        Write-Host "[OK] Old rule removed" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] Keeping existing rule" -ForegroundColor Yellow
        exit 0
    }
}

# Создание правила firewall
Write-Host "Creating firewall rule for MQTT broker (port 1883)..." -ForegroundColor Yellow
try {
    New-NetFirewallRule -DisplayName "MQTT Broker" `
        -Direction Inbound `
        -LocalPort 1883 `
        -Protocol TCP `
        -Action Allow `
        -Description "Allow MQTT broker connections from router" `
        -ErrorAction Stop
    
    Write-Host "[OK] Firewall rule created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Rule details:" -ForegroundColor Cyan
    Get-NetFirewallRule -DisplayName "MQTT Broker" | Format-List DisplayName, Enabled, Direction, Action, LocalPort
} catch {
    Write-Host "[ERROR] Failed to create firewall rule: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firewall setup complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify MQTT broker is running on port 1883" -ForegroundColor White
Write-Host "2. Check router config: /etc/scanner.conf" -ForegroundColor White
Write-Host "3. Ensure MQTT_HOST points to this PC's IP: 192.168.1.101" -ForegroundColor White
Write-Host "4. Test connection from router:" -ForegroundColor White
Write-Host "   mosquitto_pub -h 192.168.1.101 -t test -m 'test'" -ForegroundColor Cyan
Write-Host ""
