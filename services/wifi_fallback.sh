#!/bin/bash
source "$(dirname "$0")/../secrets.env"
TARGET_SSID="$WIFI_SSID"
FALLBACK_CON="$FALLBACK_SSID"

current_ssid=$(nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2)

if [ "$current_ssid" = "$TARGET_SSID" ]; then
    nmcli -t -f GENERAL.STATE connection show "$FALLBACK_CON" 2>/dev/null | grep -q activated && \
        nmcli connection down "$FALLBACK_CON"
    exit 0
fi

nmcli connection up "$TARGET_SSID" >/dev/null 2>&1 && exit 0

nmcli -t -f GENERAL.STATE connection show "$FALLBACK_CON" 2>/dev/null | grep -q activated || \
    nmcli connection up "$FALLBACK_CON"