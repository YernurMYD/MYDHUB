#!/bin/sh
# Скрипт для настройки Wi-Fi сканера на роутере OpenWrt
# Запустите этот скрипт на роутере через SSH

set -e

echo "=== Настройка Wi-Fi сканера на OpenWrt ==="

# 1. Обновление списка пакетов
echo "Обновление списка пакетов..."
opkg update

# 2. Установка необходимых пакетов
echo "Установка необходимых пакетов..."
opkg install mosquitto-client tcpdump coreutils-timeout 2>/dev/null || opkg install mosquitto-client tcpdump || {
    echo "ОШИБКА: Не удалось установить пакеты. Возможно, требуется добавить репозитории."
    echo "Попробуйте вручную: opkg install mosquitto-client tcpdump"
    exit 1
}

# 3. Проверка наличия scanner.sh
if [ ! -f "/usr/bin/scanner.sh" ]; then
    echo "ОШИБКА: Файл /usr/bin/scanner.sh не найден!"
    echo "Скопируйте scanner.sh на роутер в /usr/bin/scanner.sh"
    exit 1
fi

# 4. Установка прав на выполнение
echo "Установка прав на выполнение для scanner.sh..."
chmod +x /usr/bin/scanner.sh

# 5. Проверка конфигурации
if [ ! -f "/etc/scanner.conf" ]; then
    echo "ВНИМАНИЕ: Файл /etc/scanner.conf не найден!"
    echo "Создайте файл /etc/scanner.conf на основе scanner.conf.example"
    echo "И настройте MQTT_HOST на IP адрес вашего Windows PC"
    exit 1
fi

# 6. Проверка интерфейса мониторинга
echo "Проверка интерфейса мониторинга..."
. /etc/scanner.conf
if ! iw dev 2>/dev/null | grep -q "$INTERFACE"; then
    echo "Создание интерфейса $INTERFACE..."
    iw phy phy0 interface add "$INTERFACE" type monitor 2>/dev/null || {
        echo "ОШИБКА: Не удалось создать интерфейс $INTERFACE"
        exit 1
    }
    ifconfig "$INTERFACE" up 2>/dev/null || {
        echo "ОШИБКА: Не удалось поднять интерфейс $INTERFACE"
        exit 1
    }
fi

# 7. Установка init скрипта
if [ -f "/etc/init.d/scanner" ]; then
    echo "Init скрипт уже существует, обновление..."
else
    echo "Создание init скрипта..."
fi

# Копирование init скрипта (если он есть в текущей директории)
if [ -f "./scanner.init" ]; then
    cp ./scanner.init /etc/init.d/scanner
    chmod +x /etc/init.d/scanner
    echo "Init скрипт установлен"
else
    echo "ВНИМАНИЕ: Файл scanner.init не найден в текущей директории"
    echo "Создайте /etc/init.d/scanner вручную на основе scanner.init"
fi

# 8. Включение автозапуска
echo "Включение автозапуска..."
/etc/init.d/scanner enable

echo ""
echo "=== Настройка завершена! ==="
echo ""
echo "Для запуска сканера выполните:"
echo "  /etc/init.d/scanner start"
echo ""
echo "Для проверки статуса:"
echo "  /etc/init.d/scanner status"
echo ""
echo "Для просмотра логов:"
echo "  logread | grep scanner"
