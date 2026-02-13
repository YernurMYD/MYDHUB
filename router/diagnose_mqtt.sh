#!/bin/sh
# Скрипт диагностики проблем с передачей данных через MQTT
# Запустите на роутере: sh /tmp/diagnose_mqtt.sh

echo "========================================"
echo "MQTT Diagnostic Tool"
echo "========================================"
echo ""

# 1. Проверка конфигурации
echo "1. Checking configuration..."
if [ -f "/etc/scanner.conf" ]; then
    echo "   [OK] /etc/scanner.conf found"
    . /etc/scanner.conf
    echo "   INTERFACE: ${INTERFACE:-NOT SET}"
    echo "   MQTT_HOST: ${MQTT_HOST:-NOT SET}"
    echo "   MQTT_TOPIC: ${MQTT_TOPIC:-NOT SET}"
else
    echo "   [ERROR] /etc/scanner.conf not found!"
    exit 1
fi

# 2. Проверка интерфейса
echo ""
echo "2. Checking monitor interface..."
if iw dev 2>/dev/null | grep -q "Interface $INTERFACE"; then
    echo "   [OK] Interface $INTERFACE exists"
    if ifconfig "$INTERFACE" 2>/dev/null | grep -q "UP"; then
        echo "   [OK] Interface $INTERFACE is UP"
    else
        echo "   [WARNING] Interface $INTERFACE is DOWN"
        echo "   Trying to bring it up..."
        ifconfig "$INTERFACE" up 2>/dev/null
    fi
else
    echo "   [ERROR] Interface $INTERFACE not found!"
    echo "   Trying to create it..."
    iw phy phy0 interface add "$INTERFACE" type monitor 2>/dev/null
    ifconfig "$INTERFACE" up 2>/dev/null
fi

# 3. Проверка установленных пакетов
echo ""
echo "3. Checking required packages..."
if command -v mosquitto_pub >/dev/null 2>&1; then
    echo "   [OK] mosquitto_pub installed"
    mosquitto_pub -V 2>/dev/null || echo "   Version: unknown"
else
    echo "   [ERROR] mosquitto_pub not found!"
    echo "   Install with: opkg install mosquitto-client"
fi

if command -v tcpdump >/dev/null 2>&1; then
    echo "   [OK] tcpdump installed"
else
    echo "   [ERROR] tcpdump not found!"
    echo "   Install with: opkg install tcpdump"
fi

# 4. Проверка сетевой доступности MQTT брокера
echo ""
echo "4. Checking network connectivity to MQTT broker..."
if [ -z "$MQTT_HOST" ]; then
    echo "   [ERROR] MQTT_HOST not set in config!"
else
    echo "   Testing ping to $MQTT_HOST..."
    if ping -c 2 "$MQTT_HOST" >/dev/null 2>&1; then
        echo "   [OK] Host $MQTT_HOST is reachable"
    else
        echo "   [ERROR] Cannot ping $MQTT_HOST"
        echo "   Check network connectivity and IP address"
    fi
    
    echo "   Testing MQTT connection to $MQTT_HOST:1883..."
    if echo "test" | mosquitto_pub -h "$MQTT_HOST" -t "test/connection" -l 2>&1 | grep -q "Error"; then
        echo "   [ERROR] Cannot connect to MQTT broker"
        echo "   Common issues:"
        echo "   - MQTT broker not running on $MQTT_HOST"
        echo "   - Firewall blocking port 1883"
        echo "   - Wrong IP address"
    else
        echo "   [OK] MQTT connection successful"
    fi
fi

# 5. Проверка процесса scanner
echo ""
echo "5. Checking scanner process..."
if pgrep -f scanner.sh >/dev/null; then
    echo "   [OK] scanner.sh is running"
    ps aux | grep scanner.sh | grep -v grep
else
    echo "   [WARNING] scanner.sh is not running"
    echo "   Start with: /etc/init.d/scanner start"
fi

# 6. Проверка логов
echo ""
echo "6. Recent scanner logs..."
logread | grep -i scanner | tail -10 || echo "   No scanner logs found"

# 7. Тестовая отправка сообщения
echo ""
echo "7. Testing MQTT publish..."
if [ -n "$MQTT_HOST" ] && [ -n "$MQTT_TOPIC" ]; then
    TEST_MSG='{"t":'$(date +%s)',"d":[{"m":"aa:bb:cc:dd:ee:ff","r":-63,"x":0}],"c":1}'
    echo "   Sending test message: $TEST_MSG"
    if echo "$TEST_MSG" | mosquitto_pub -h "$MQTT_HOST" -t "$MQTT_TOPIC" -l 2>&1; then
        echo "   [OK] Test message sent successfully"
    else
        echo "   [ERROR] Failed to send test message"
        echo "   Check MQTT broker and network connectivity"
    fi
else
    echo "   [SKIP] MQTT_HOST or MQTT_TOPIC not configured"
fi

# 8. Проверка захвата пакетов
echo ""
echo "8. Testing packet capture..."
if [ -n "$INTERFACE" ]; then
    echo "   Capturing 5 probe requests from $INTERFACE (timeout 10s)..."
    timeout 10 tcpdump -i "$INTERFACE" -e -n -s 256 -c 5 "type mgt subtype probe-req" 2>&1 | head -5
    if [ $? -eq 0 ]; then
        echo "   [OK] Packet capture working"
    else
        echo "   [WARNING] No packets captured (may be normal if no devices nearby)"
    fi
fi

echo ""
echo "========================================"
echo "Diagnostic complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Check /etc/scanner.conf - ensure MQTT_HOST is correct"
echo "2. Verify MQTT broker is running on Windows PC"
echo "3. Check Windows firewall allows port 1883"
echo "4. Test manually: mosquitto_pub -h <IP> -t wifi/probes -m '{\"t\":123,\"d\":[],\"c\":0}'"
echo "5. Check logs: logread | grep scanner"
echo ""
