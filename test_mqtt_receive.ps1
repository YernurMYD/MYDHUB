# Скрипт для проверки получения MQTT сообщений на Windows PC
# Запустите этот скрипт перед отправкой сообщения с роутера

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MQTT Message Receiver Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Listening for MQTT messages on topic 'test'..." -ForegroundColor Yellow
Write-Host "Send message from router with:" -ForegroundColor Cyan
Write-Host "  mosquitto_pub -h 192.168.1.101 -t test -m 'test'" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Проверка наличия mosquitto_sub
if (-not (Get-Command mosquitto_sub -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] mosquitto_sub not found!" -ForegroundColor Red
    Write-Host "Install Mosquitto client tools or use Docker:" -ForegroundColor Yellow
    Write-Host "  docker run -it --rm eclipse-mosquitto mosquitto_sub -h host.docker.internal -t test" -ForegroundColor Cyan
    exit 1
}

# Подписка на топик
try {
    mosquitto_sub -h localhost -t test -v
} catch {
    Write-Host "[ERROR] Failed to subscribe: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Use Python script (test_mqtt_receive.py)" -ForegroundColor Yellow
}
