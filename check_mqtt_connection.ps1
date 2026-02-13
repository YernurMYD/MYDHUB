# Скрипт проверки подключения MQTT брокера с Windows PC
# Проверяет доступность брокера и возможность получения сообщений

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MQTT Connection Check (Windows PC)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Проверка MQTT брокера
Write-Host "1. Checking MQTT broker..." -ForegroundColor Yellow
$mqttCheck = Test-NetConnection -ComputerName localhost -Port 1883 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($mqttCheck) {
    Write-Host "   [OK] MQTT broker is listening on port 1883" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] MQTT broker is not accessible on port 1883" -ForegroundColor Red
    Write-Host "   Start Mosquitto or check if it's running" -ForegroundColor Yellow
}

# 2. Проверка IP адреса для роутера
Write-Host ""
Write-Host "2. Checking network configuration..." -ForegroundColor Yellow
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -ExpandProperty IPAddress
Write-Host "   Available IP addresses:" -ForegroundColor Cyan
foreach ($ip in $ipAddresses) {
    Write-Host "     - $ip" -ForegroundColor White
}
Write-Host ""
Write-Host "   IMPORTANT: Use one of these IPs in /etc/scanner.conf on router" -ForegroundColor Yellow
Write-Host "   Example: MQTT_HOST=`"$($ipAddresses[0])`"" -ForegroundColor Cyan

# 3. Проверка firewall
Write-Host ""
Write-Host "3. Checking Windows Firewall..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "*MQTT*" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "   [INFO] Found MQTT firewall rules" -ForegroundColor Cyan
    $firewallRule | Format-Table DisplayName, Enabled, Direction
} else {
    Write-Host "   [WARNING] No specific MQTT firewall rules found" -ForegroundColor Yellow
    Write-Host "   Port 1883 may be blocked by firewall" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   To allow port 1883, run as Administrator:" -ForegroundColor Cyan
    Write-Host "   New-NetFirewallRule -DisplayName 'MQTT Broker' -Direction Inbound -LocalPort 1883 -Protocol TCP -Action Allow" -ForegroundColor White
}

# 4. Тестовая подписка на топик
Write-Host ""
Write-Host "4. Testing MQTT subscription..." -ForegroundColor Yellow
Write-Host "   Starting subscription to 'wifi/probes' topic (10 seconds)..." -ForegroundColor Cyan
Write-Host "   Send test message from router to see if it arrives" -ForegroundColor Yellow
Write-Host ""

$testSub = Start-Job -ScriptBlock {
    param($hostname, $topic)
    if (Get-Command mosquitto_sub -ErrorAction SilentlyContinue) {
        mosquitto_sub -h $hostname -t $topic -W 10 2>&1
    } else {
        Write-Output "mosquitto_sub not found. Install Mosquitto client tools."
    }
} -ArgumentList "localhost", "wifi/probes"

Start-Sleep -Seconds 2

# Отправка тестового сообщения
Write-Host "   Sending test message..." -ForegroundColor Cyan
if (Get-Command mosquitto_pub -ErrorAction SilentlyContinue) {
    $testMsg = '{"t":' + [int][double]::Parse((Get-Date -UFormat %s)) + ',"d":[{"m":"aa:bb:cc:dd:ee:ff","r":-63,"x":0}],"c":1}'
    mosquitto_pub -h localhost -t "wifi/probes" -m $testMsg 2>&1 | Out-Null
    Write-Host "   [OK] Test message sent" -ForegroundColor Green
} else {
    Write-Host "   [WARNING] mosquitto_pub not found" -ForegroundColor Yellow
}

# Ожидание результата подписки
$result = Wait-Job $testSub | Receive-Job
Remove-Job $testSub -Force

if ($result) {
    Write-Host "   [OK] Message received: $result" -ForegroundColor Green
} else {
    Write-Host "   [WARNING] No message received (may be normal if no messages sent)" -ForegroundColor Yellow
}

# 5. Инструкции для роутера
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Router Configuration Checklist" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "On the router, verify:" -ForegroundColor Yellow
Write-Host "1. /etc/scanner.conf has correct MQTT_HOST (use IP from step 2)" -ForegroundColor White
Write-Host "2. Test connection: mosquitto_pub -h <IP_PC> -t test -m 'test'" -ForegroundColor White
Write-Host "3. Check scanner logs: logread | grep scanner" -ForegroundColor White
Write-Host "4. Check if scanner is capturing: tcpdump -i mon0 -c 5 'type mgt subtype probe-req'" -ForegroundColor White
Write-Host "5. Run diagnostic script on router:" -ForegroundColor White
Write-Host "   sh /tmp/diagnose_mqtt.sh" -ForegroundColor Cyan
Write-Host ""
