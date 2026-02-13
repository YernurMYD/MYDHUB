#!/bin/sh

# ---------------------------
# Wi-Fi Probe Requests Scanner (OpenWrt / BusyBox sh)
# - Monitor interface: mon0 (or from /etc/scanner.conf)
# - Captures Probe Requests via tcpdump (BPF: type mgt subtype probe-req)
# - Channel hopping: 1 / 6 / 11
# - Sends JSON to MQTT: {"t":unix_ts,"d":[{"m":"..","r":-63,"x":1},...],"c":N}
# - CYCLE_TIME: отправка каждые N сек (по умолчанию 600 = 10 минут)
# - Локальный буфер: если MQTT недоступен, данные сохраняются и досылаются позже
# ---------------------------

CONFIG_FILE="/etc/scanner.conf"

# ---- Load config ----
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
else
    echo "Error: $CONFIG_FILE not found" >&2
    exit 1
fi

# ---- Required config ----
if [ -z "$INTERFACE" ] || [ -z "$MQTT_HOST" ] || [ -z "$MQTT_TOPIC" ]; then
    echo "Error: Missing required config in $CONFIG_FILE (INTERFACE/MQTT_HOST/MQTT_TOPIC)" >&2
    exit 1
fi

# ---- Defaults ----
# CYCLE_TIME: интервал отправки в секундах (по умолчанию 600 = каждые 10 минут)
# Роутер агрегирует данные и отправляет раз в CYCLE_TIME секунд — для графика с шагом 10 мин
CYCLE_TIME=${CYCLE_TIME:-600}

# packets per channel (per cycle); high limit, cycle controlled by timeout
PACKETS_PER_CH=${PACKETS_PER_CH:-500}

# channels to hop
CHANNELS=${CHANNELS:-"1 6 11"}

# Рабочий канал AP (чтобы вернуть радио после channel hopping)
# Определяем автоматически или берём из конфига
HOME_CHANNEL=${HOME_CHANNEL:-""}

# Время ожидания восстановления сети после channel hopping (сек)
NETWORK_SETTLE_TIME=${NETWORK_SETTLE_TIME:-15}

# MQTT retry: кол-во попыток и начальная задержка (экспоненциальная)
MQTT_RETRIES=${MQTT_RETRIES:-5}
MQTT_RETRY_DELAY=${MQTT_RETRY_DELAY:-3}

# Максимальное ожидание доступности хоста (сек)
HOST_WAIT_TIMEOUT=${HOST_WAIT_TIMEOUT:-120}

# Локальный буфер для неотправленных сообщений (макс. файлов)
BUFFER_DIR="/tmp/scanner_buffer"
BUFFER_MAX=${BUFFER_MAX:-10}

# seconds per channel = CYCLE_TIME / number of channels
CH_SEC=$((CYCLE_TIME / 3))
[ "$CH_SEC" -lt 1 ] && CH_SEC=1

TEMP_FILE="/tmp/probes.raw"

# ---- Создать директорию буфера ----
mkdir -p "$BUFFER_DIR"

# ---- Ensure monitor interface exists and is up ----
check_interface() {
    if ! iw dev 2>/dev/null | grep -q "Interface $INTERFACE"; then
        # Try to create monitor interface on phy0
        iw phy phy0 interface add "$INTERFACE" type monitor 2>/dev/null
    fi
    ifconfig "$INTERFACE" up 2>/dev/null
}

# ---- Определить рабочий канал AP (однократно) ----
detect_home_channel() {
    if [ -z "$HOME_CHANNEL" ]; then
        # Попробуем определить канал основного интерфейса (wlan0)
        HOME_CHANNEL="$(iw dev wlan0 info 2>/dev/null | awk '/channel/{print $2; exit}')"
        [ -z "$HOME_CHANNEL" ] && HOME_CHANNEL="6"
        logger -t scanner.sh -p daemon.info "Home channel detected: $HOME_CHANNEL"
    fi
}

# ---- Восстановить сеть после channel hopping ----
restore_network() {
    # Вернуть мониторный интерфейс на рабочий канал AP
    iw dev "$INTERFACE" set channel "$HOME_CHANNEL" 2>/dev/null
    logger -t scanner.sh -p daemon.info "Restored channel to $HOME_CHANNEL, waiting ${NETWORK_SETTLE_TIME}s for network settle"
    sleep "$NETWORK_SETTLE_TIME"
}

# ---- Ожидание доступности хоста с прогрессивным таймаутом ----
wait_for_host() {
    ELAPSED=0
    WAIT_INTERVAL=3
    while [ "$ELAPSED" -lt "$HOST_WAIT_TIMEOUT" ]; do
        ping -c 1 -W 2 "$MQTT_HOST" >/dev/null 2>&1 && return 0
        [ "$ELAPSED" -eq 0 ] && logger -t scanner.sh -p daemon.warn "Host $MQTT_HOST unreachable, waiting (max ${HOST_WAIT_TIMEOUT}s)..."
        sleep "$WAIT_INTERVAL"
        ELAPSED=$((ELAPSED + WAIT_INTERVAL))
        # Увеличиваем интервал (3, 5, 8, 10, 10...)
        [ "$WAIT_INTERVAL" -lt 10 ] && WAIT_INTERVAL=$((WAIT_INTERVAL + 2))
    done
    logger -t scanner.sh -p daemon.err "Host $MQTT_HOST unreachable after ${HOST_WAIT_TIMEOUT}s"
    return 1
}

# ---- Отправка MQTT с экспоненциальной задержкой ----
mqtt_publish() {
    PAYLOAD_FILE="$1"
    DELAY="$MQTT_RETRY_DELAY"
    i=1
    while [ "$i" -le "$MQTT_RETRIES" ]; do
        MQTT_ERR="$(mosquitto_pub -h "$MQTT_HOST" -t "$MQTT_TOPIC" -f "$PAYLOAD_FILE" -q 1 2>&1)"
        if [ $? -eq 0 ]; then
            logger -t scanner.sh -p daemon.info "MQTT publish OK (payload $(wc -c < "$PAYLOAD_FILE") bytes)"
            return 0
        fi
        logger -t scanner.sh -p daemon.warn "MQTT attempt $i/$MQTT_RETRIES failed: $MQTT_ERR"
        sleep "$DELAY"
        # Экспоненциальная задержка: 3, 6, 12, 24... (макс 30с)
        DELAY=$((DELAY * 2))
        [ "$DELAY" -gt 30 ] && DELAY=30
        i=$((i + 1))
    done
    logger -t scanner.sh -p daemon.err "MQTT publish failed after $MQTT_RETRIES attempts"
    return 1
}

# ---- Сохранить payload в локальный буфер ----
buffer_save() {
    PAYLOAD_FILE="$1"
    BUFNAME="$(date +%s).json"
    cp "$PAYLOAD_FILE" "$BUFFER_DIR/$BUFNAME"
    logger -t scanner.sh -p daemon.info "Payload buffered as $BUFNAME"
    # Очистить старые файлы если буфер переполнен
    BUFCOUNT="$(ls "$BUFFER_DIR"/*.json 2>/dev/null | wc -l)"
    while [ "$BUFCOUNT" -gt "$BUFFER_MAX" ]; do
        OLDEST="$(ls -t "$BUFFER_DIR"/*.json 2>/dev/null | tail -1)"
        [ -z "$OLDEST" ] && break
        rm -f "$OLDEST"
        BUFCOUNT=$((BUFCOUNT - 1))
    done
}

# ---- Отправить буферизованные сообщения ----
flush_buffer() {
    for BFILE in $(ls -t "$BUFFER_DIR"/*.json 2>/dev/null); do
        [ ! -f "$BFILE" ] && continue
        mqtt_publish "$BFILE"
        if [ $? -eq 0 ]; then
            rm -f "$BFILE"
        else
            # Если не удалось — прекращаем досылку, попробуем в следующий цикл
            logger -t scanner.sh -p daemon.warn "Buffer flush stopped, will retry next cycle"
            return 1
        fi
    done
    return 0
}

# ---- Main loop ----
detect_home_channel

while true; do
    check_interface

    # Timestamp for this pass
    TS="$(date +%s)"

    # Reset temp file
    : > "$TEMP_FILE"

    # Capture probe-req on multiple channels (timeout = CYCLE_TIME/3 сек на канал)
    for ch in $CHANNELS; do
        iw dev "$INTERFACE" set channel "$ch" 2>/dev/null

        # Capture probe requests: max CH_SEC sec per channel, or PACKETS_PER_CH packets
        if command -v timeout >/dev/null 2>&1; then
            timeout "$CH_SEC" tcpdump -i "$INTERFACE" -e -n -s 256 -c "$PACKETS_PER_CH" \
            "type mgt subtype probe-req" >> "$TEMP_FILE" 2>/dev/null || \
            timeout -t "$CH_SEC" tcpdump -i "$INTERFACE" -e -n -s 256 -c "$PACKETS_PER_CH" \
            "type mgt subtype probe-req" >> "$TEMP_FILE" 2>/dev/null || \
            tcpdump -i "$INTERFACE" -e -n -s 256 -c "$PACKETS_PER_CH" \
            "type mgt subtype probe-req" >> "$TEMP_FILE" 2>/dev/null
        else
            # Без timeout: tcpdump в фоне, sleep CH_SEC, kill — цикл ограничен по времени
            tcpdump -i "$INTERFACE" -e -n -s 256 -c "$PACKETS_PER_CH" \
            "type mgt subtype probe-req" >> "$TEMP_FILE" 2>/dev/null &
            TD_PID=$!
            sleep "$CH_SEC"
            kill $TD_PID 2>/dev/null
            wait $TD_PID 2>/dev/null
        fi
    done

    # ---- Восстановить сеть после channel hopping ----
    restore_network

    # Build JSON payload from captured lines
    JSON_PAYLOAD="$(
    awk -v ts="$TS" '
    {
        # RSSI: look for -NNdBm (tcpdump radiotap prints like -40dBm)
        if (match($0, /-[0-9]+dBm/)) {
            rssi = substr($0, RSTART, RLENGTH-3)   # keep minus, remove "dBm"
        } else {
            next
        }

        # Source MAC can appear as SA:xx:... or "SA:xx:.." in many tcpdump formats
        if (match($0, /SA:[0-9a-fA-F:]{17}/)) {
            mac = substr($0, RSTART+3, 17)
        } else {
            # Some builds may show "SA xx:xx..." without colon after SA, try fallback:
            if (match($0, /SA [0-9a-fA-F:]{17}/)) {
                mac = substr($0, RSTART+3, 17)
            } else {
                next
            }
        }

        if (mac != "") {
            # Random MAC check: locally administered bit (2nd hex nibble in first byte)
            # aa:.. -> second char is "a"
            char2 = substr(mac, 2, 1)
            is_random = (char2 ~ /[26AaEe]/) ? 1 : 0

            # Keep best (max) RSSI per MAC
            if (!(mac in max_rssi) || rssi > max_rssi[mac]) {
                max_rssi[mac] = rssi
                random_flag[mac] = is_random
            }
        }
    }
    END {
        c = 0
        printf "{\"t\":%d,\"d\":[", ts
        first = 1
        for (m in max_rssi) {
            if (!first) printf ","
            printf "{\"m\":\"%s\",\"r\":%d,\"x\":%d}", m, max_rssi[m], random_flag[m]
            first = 0
            c++
        }
        printf "],\"c\":%d}", c
    }' "$TEMP_FILE"
    )"

    # Записываем payload в файл, чтобы обойти лимит длины аргументов shell
    MQTT_PAYLOAD_FILE="/tmp/mqtt_payload.json"
    echo "$JSON_PAYLOAD" > "$MQTT_PAYLOAD_FILE"

    # ---- Ждём доступности хоста ----
    if wait_for_host; then
        # Сначала досылаем буферизованные данные
        flush_buffer

        # Отправляем текущий payload
        if mqtt_publish "$MQTT_PAYLOAD_FILE"; then
            rm -f "$MQTT_PAYLOAD_FILE"
        else
            # Не удалось — сохраняем в буфер
            buffer_save "$MQTT_PAYLOAD_FILE"
            rm -f "$MQTT_PAYLOAD_FILE"
        fi
    else
        # Хост недоступен — сохраняем в буфер для досылки
        buffer_save "$MQTT_PAYLOAD_FILE"
        rm -f "$MQTT_PAYLOAD_FILE"
    fi

    # Cleanup
    rm -f "$TEMP_FILE"

    SLEEP_BETWEEN_PASSES=${SLEEP_BETWEEN_PASSES:-0}
    [ "$SLEEP_BETWEEN_PASSES" -gt 0 ] && sleep "$SLEEP_BETWEEN_PASSES"
done
