#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source secrets.env

# $WIFI_SSID: normal client connection, higher priority
sudo nmcli connection add type wifi ifname wlan0 con-name "$WIFI_SSID" ssid "$WIFI_SSID" \
    connection.autoconnect yes connection.autoconnect-priority 10 \
    wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PASSWORD" 2>/dev/null || \
    sudo nmcli connection modify "$WIFI_SSID" wifi-sec.psk "$WIFI_PASSWORD"

# $FALLBACK_SSID: fallback hotspot, does NOT autoconnect (the watchdog brings it up manually)
sudo nmcli connection add type wifi ifname wlan0 con-name "$FALLBACK_SSID" ssid "$FALLBACK_SSID" \
    connection.autoconnect no \
    802-11-wireless.mode ap 802-11-wireless.band bg \
    ipv4.method shared \
    wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$FALLBACK_PASSWORD" 2>/dev/null || \
    sudo nmcli connection modify "$FALLBACK_SSID" wifi-sec.psk "$FALLBACK_PASSWORD"

echo "Wifi profiles configured."