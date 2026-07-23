#!/bin/bash
source "$(dirname "$0")/../secrets.env"
TARGET_SSID="$WIFI_SSID"
FALLBACK_CON="$FALLBACK_SSID"
WLAN_DEV="wlan0"
RETRY_STATE_FILE="/tmp/vtg_wifi_last_retry"
RETRY_INTERVAL=300   # only re-check primary every 5 min while on fallback, to stop flapping

active_con=$(nmcli -t -f NAME,DEVICE connection show --active | awk -F: -v dev="$WLAN_DEV" '$2==dev {print $1}')

if [ "$active_con" = "$TARGET_SSID" ]; then
    rm -f "$RETRY_STATE_FILE"
    exit 0
fi

if [ "$active_con" = "$FALLBACK_CON" ]; then
    now=$(date +%s)
    last=$(cat "$RETRY_STATE_FILE" 2>/dev/null || echo 0)
    if [ $((now - last)) -lt "$RETRY_INTERVAL" ]; then
        exit 0
    fi
    echo "$now" > "$RETRY_STATE_FILE"
fi

if nmcli connection up "$TARGET_SSID" >/dev/null 2>&1; then
    rm -f "$RETRY_STATE_FILE"
    exit 0
fi

nmcli connection up "$FALLBACK_CON" >/dev/null 2>&1