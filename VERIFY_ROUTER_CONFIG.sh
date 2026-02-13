#!/bin/sh
# Скрипт для проверки конфигурации на роутере
# Запустите на роутере: sh /tmp/VERIFY_ROUTER_CONFIG.sh

echo "========================================"
echo "Router Configuration Verification"
echo "========================================"
echo ""
echo "Router IP: 192.168.1.100"
echo "Windows PC IP: 192.168.1.101"
echo ""

# Проверка конфигурации
echo "1. Checking /etc/scanner.conf..."
if [ -f "/etc/scanner.conf" ]; then
    echo "   [OK] Configuration file exists"
    echo ""
    echo "   Current configuration:"
    cat /etc/scanner.conf | grep -E "^(INTERFACE|MQTT_HOST|MQTT_TOPIC)="
    echo ""
    
    . /etc/scanner.conf
    
    if [ "$MQTT_HOST" = "192.168.1.101" ]; then
        echo "   [OK] MQTT_HOST is correct: $MQTT_HOST"
    else
        echo "   [ERROR] MQTT_HOST is incorrect: $MQTT_HOST"
        echo "   Should be: 192.168.1.101"
        echo ""
        echo "   To fix, edit /etc/scanner.conf:"
        echo "   vi /etc/scanner.conf"
        echo "   Change: MQTT_HOST=\"192.168.1.101\""
    fi
else
    echo "   [ERROR] Configuration file not found!"
    echo "   Create it: cp /etc/scanner.conf.example /etc/scanner.conf"
fi

# Проверка подключения к Windows PC
echo ""
echo "2. Testing connection to Windows PC (192.168.1.101)..."
if ping -c 2 192.168.1.101 >/dev/null 2>&1; then
    echo "   [OK] Windows PC is reachable"
else
    echo "   [ERROR] Cannot ping Windows PC"
    echo "   Check network connectivity"
fi

# Проверка MQTT подключения
echo ""
echo "3. Testing MQTT connection..."
if command -v mosquitto_pub >/dev/null 2>&1; then
    if echo "test" | mosquitto_pub -h 192.168.1.101 -t "test/verify" -l 2>&1 | grep -q "Error"; then
        echo "   [ERROR] Cannot connect to MQTT broker"
        echo "   Possible issues:"
        echo "   - Firewall blocking port 1883 on Windows PC"
        echo "   - MQTT broker not running"
        echo "   - Wrong IP address"
    else
        echo "   [OK] MQTT connection successful"
    fi
else
    echo "   [WARNING] mosquitto_pub not found"
    echo "   Install: opkg install mosquitto-client"
fi

# Проверка интерфейса
echo ""
echo "4. Checking monitor interface..."
if [ -n "$INTERFACE" ]; then
    if iw dev 2>/dev/null | grep -q "Interface $INTERFACE"; then
        echo "   [OK] Interface $INTERFACE exists"
        if ifconfig "$INTERFACE" 2>/dev/null | grep -q "UP"; then
            echo "   [OK] Interface $INTERFACE is UP"
        else
            echo "   [WARNING] Interface $INTERFACE is DOWN"
        fi
    else
        echo "   [ERROR] Interface $INTERFACE not found"
    fi
fi

# Проверка процесса scanner
echo ""
echo "5. Checking scanner process..."
if pgrep -f scanner.sh >/dev/null; then
    echo "   [OK] scanner.sh is running"
    ps aux | grep scanner.sh | grep -v grep
else
    echo "   [WARNING] scanner.sh is not running"
    echo "   Start with: /etc/init.d/scanner start"
fi

echo ""
echo "========================================"
echo "Verification complete!"
echo "========================================"
echo ""
