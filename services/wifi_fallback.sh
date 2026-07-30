#!/bin/bash
source "$(dirname "$0")/../secrets.env"
TARGET_SSID="$WIFI_SSID"
FALLBACK_CON="$FALLBACK_SSID"
WLAN_DEV="wlan0"

# Clear a stuck/hung connection attempt before doing anything else
nmcli -t -f GENERAL.STATE device show "$WLAN_DEV" | grep -q "connecting" && nmcli device disconnect "$WLAN_DEV"

active_con=$(nmcli -t -f NAME,DEVICE connection show --active | awk -F: -v dev="$WLAN_DEV" '$2==dev {print $1}')

# Already settled on something -- never touch it again until reboot.
if [ -n "$active_con" ]; then
    exit 0
fi

# Not connected to anything -- decide once: try the target, else fall back.
if timeout 15 nmcli connection up "$TARGET_SSID" >/dev/null 2>&1; then
    exit 0
fi

nmcli connection up "$FALLBACK_CON" >/dev/null 2>&1