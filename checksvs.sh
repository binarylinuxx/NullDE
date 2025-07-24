#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVICES=("dbus" "seatd" "elogind")

check_and_fix() {
    local service=$1
    
    if sudo sv status "$service" 2>/dev/null | grep -q "run"; then
        echo -e "${GREEN}[+] $service${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}[!] $service not running, fixing...${NC}"
    
    # Install if missing
    sudo xbps-install -y "$service" 2>/dev/null
    
    # Enable and start
    sudo ln -sf /etc/sv/"$service" /var/service/ 2>/dev/null
    sudo sv up "$service" 2>/dev/null
    
    if sudo sv status "$service" 2>/dev/null | grep -q "run"; then
        echo -e "${GREEN}[+] $service fixed${NC}"
    else
        echo -e "${RED}[-] $service failed${NC}"
        return 1
    fi
}

check_user_groups() {
    local groups=("video" "_seatd")
    
    for group in "${groups[@]}"; do
        if ! groups "$USER" | grep -q "$group"; then
            echo -e "${YELLOW}[!] Adding $USER to $group group${NC}"
            if sudo usermod -aG "$group" "$USER" 2>/dev/null; then
                echo -e "${GREEN}[+] Added to $group group${NC}"
            else
                echo -e "${RED}[-] Failed to add to $group group${NC}"
            fi
        fi
    done
}

next_script() {
	source install_font_and_shell.sh
}

main() {
    echo "Checking Hyprland services..."
    
    check_user_groups
    
    # Check services
    local failed=0
    for service in "${SERVICES[@]}"; do
        check_and_fix "$service" || ((failed++))
    done
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}[+] All services OK. Reboot recommended.${NC}"
    else
        echo -e "${RED}[-] $failed services failed${NC}"
        exit 1
    fi
    next_script
}

main
