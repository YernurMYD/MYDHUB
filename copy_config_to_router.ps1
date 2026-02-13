# Скрипт для копирования конфигурации scanner на роутер
# Упрощает процесс создания /etc/scanner.conf

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Copy Scanner Config to Router" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$routerIP = "192.168.1.100"
$configFile = "router/scanner.conf.example"
$remotePath = "/etc/scanner.conf"

# Проверка наличия файла
if (-not (Test-Path $configFile)) {
    Write-Host "[ERROR] Config file not found: $configFile" -ForegroundColor Red
    exit 1
}

Write-Host "Router IP: $routerIP" -ForegroundColor Yellow
Write-Host "Config file: $configFile" -ForegroundColor Yellow
Write-Host "Remote path: $remotePath" -ForegroundColor Yellow
Write-Host ""

# Копирование файла
Write-Host "Copying config file to router..." -ForegroundColor Yellow
try {
    scp $configFile "root@${routerIP}:${remotePath}"
    Write-Host "[OK] Config file copied successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to copy config file: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. SSH key is set up for passwordless login" -ForegroundColor White
    Write-Host "2. Router is accessible at $routerIP" -ForegroundColor White
    Write-Host "3. Or copy manually:" -ForegroundColor White
    Write-Host "   scp router/scanner.conf.example root@${routerIP}:/etc/scanner.conf" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "Next steps on router:" -ForegroundColor Cyan
Write-Host "1. Verify config: cat /etc/scanner.conf" -ForegroundColor White
Write-Host "2. Edit if needed: vi /etc/scanner.conf" -ForegroundColor White
Write-Host "3. Restart scanner: /etc/init.d/scanner restart" -ForegroundColor White
Write-Host "4. Check status: /etc/init.d/scanner status" -ForegroundColor White
Write-Host ""
