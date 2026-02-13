# Скрипт для создания конфигурации scanner через SSH (без SCP)
# Использует SSH команды для создания файла напрямую на роутере

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Create Scanner Config via SSH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$routerIP = "192.168.1.100"
$configContent = @"
INTERFACE="mon0"
MQTT_HOST="192.168.1.101"
MQTT_TOPIC="wifi/probes"
"@

Write-Host "Router IP: $routerIP" -ForegroundColor Yellow
Write-Host "Creating /etc/scanner.conf..." -ForegroundColor Yellow
Write-Host ""

# Создание файла через SSH с использованием heredoc
$sshCommand = @"
cat > /etc/scanner.conf << 'EOF'
INTERFACE="mon0"
MQTT_HOST="192.168.1.101"
MQTT_TOPIC="wifi/probes"
EOF
cat /etc/scanner.conf
"@

Write-Host "Executing SSH command..." -ForegroundColor Cyan
Write-Host ""

try {
    # Выполнение команды через SSH
    $result = ssh root@${routerIP} $sshCommand 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Config file created successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "File contents:" -ForegroundColor Cyan
        Write-Host $result
    } else {
        Write-Host "[ERROR] Failed to create config file" -ForegroundColor Red
        Write-Host $result
        Write-Host ""
        Write-Host "Try manual method:" -ForegroundColor Yellow
        Write-Host "  ssh root@${routerIP}" -ForegroundColor White
        Write-Host "  Then run:" -ForegroundColor White
        Write-Host '  cat > /etc/scanner.conf << "EOF"' -ForegroundColor Cyan
        Write-Host '  INTERFACE="mon0"' -ForegroundColor Cyan
        Write-Host '  MQTT_HOST="192.168.1.101"' -ForegroundColor Cyan
        Write-Host '  MQTT_TOPIC="wifi/probes"' -ForegroundColor Cyan
        Write-Host '  EOF' -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "[ERROR] SSH connection failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. Router is accessible at $routerIP" -ForegroundColor White
    Write-Host "2. SSH is enabled on router" -ForegroundColor White
    Write-Host "3. You have root password" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart scanner: ssh root@${routerIP} '/etc/init.d/scanner restart'" -ForegroundColor White
Write-Host "2. Check status: ssh root@${routerIP} '/etc/init.d/scanner status'" -ForegroundColor White
Write-Host "3. Check logs: ssh root@${routerIP} 'logread | grep scanner | tail -20'" -ForegroundColor White
Write-Host ""
