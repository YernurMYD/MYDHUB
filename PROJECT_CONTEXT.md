# PROJECT CONTEXT

Проект: Пассивный Wi-Fi мониторинг (Probe Requests)

Edge-устройство:
- TP-Link MR3020 v3
- CPU: AR9331
- RAM: 64MB
- OS: OpenWrt 22.03.x
- Interface: mon0 (monitor mode)

Текущий статус:
- tcpdump -i mon0 -e -n | grep probe работает
- Сбор только probe request
- Устройства не подключаются к AP
- Сбор пассивный, легальный

Ограничения edge:
- Минимум RAM
- Только busybox / awk / shell
- Без Python, без JSON-библиотек
- Агрегация данных на edge (60 сек)

Формат данных:
- Unix timestamp (UTC, seconds)
- Один timestamp на цикл агрегации
- JSON минимальный

Транспорт:
- MQTT
- MR3020 → ПК на Windows

Сервер:
- ПК под Windows
- Принимает MQTT
- Готовит API
- В будущем: коммерческий web-дашборд

Цель:
- Сбор MAC + RSSI
- Подсчёт уникальных устройств
- Реальное время
- Масштабирование и продажа данных
