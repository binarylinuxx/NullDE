#!/bin/bash

# Network status script with Nerd Font icons

get_wifi_icon() {
    if [ -z "$1" ]; then
        echo "󰤭"  # No connection
        return
    fi

    case $1 in
        *5[0-9]|*6[0-9]|*7[0-9]|*8[0-9]|*9[0-9]|100) echo "󰤨" ;;  # Strong
        *4[0-9]|*3[0-9]) echo "󰤥" ;;  # Normal
        *2[0-9]|*1[0-9]) echo "󰤢" ;;  # Almost normal
        *[1-9]) echo "󰤟" ;;  # Weak
        *) echo "󰤭" ;;  # No connection
    esac
}

get_wired_icon() {
    if ip link show up | grep -q "state UP"; then
        echo " - Wired"  # Connected
    else
        echo "󰈂 - Wired no connection"  # No connection
    fi
}

# Main logic
if ip route | grep -q default; then
    if ip route | grep default | grep -q wlan; then
        # WiFi connection
        ssid=$(iwgetid -r)
        if [ -z "$ssid" ]; then
            echo "󰤭"
        else
            strength=$(awk '/^\s*w/ { print int($3 * 100 / 70) }' /proc/net/wireless)
            get_wifi_icon "$strength"
        fi
    else
        # Wired connection
        get_wired_icon
    fi
else
    # No network connection
    echo "󰤭"
fi
