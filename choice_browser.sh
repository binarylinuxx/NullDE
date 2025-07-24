#!/bin/bash

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Проверка root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}[-] This script must be run as root${NC}"
        exit 1
    fi
}

# Установка через xbps
install_packages() {
    echo -e "${CYAN}[+] Updating package database...${NC}"
    sudo xbps-install -Suy || {
        echo -e "${RED}[-] Failed to update packages${NC}"
        exit 1
    }

    echo -e "${CYAN}[+] Installing base packages...${NC}"
    sudo xbps-install -y git make gcc pkg-config || {
        echo -e "${RED}[-] Failed to install base packages${NC}"
        exit 1
    }
}

# Выбор браузера
select_browser() {
    echo -e "${CYAN}[!] Choose browser to install${NC}"
    echo -e "${YELLOW}[1] Firefox"
    echo -e "[2] Chromium"
    echo -e "[3] qutebrowser (minimal)${NC}"
    echo -ne "${YELLOW}Select [1-3]: ${NC}"

    read -r choice
    case $choice in
        1)
            echo -e "${GREEN}[+] Installing Firefox...${NC}"
            sudo xbps-install -y firefox || echo -e "${RED}[-] Failed to install Firefox${NC}"
            ;;
        2)
            echo -e "${GREEN}[+] Installing Chromium...${NC}"
            sudo xbps-install -y chromium || echo -e "${RED}[-] Failed to install Chromium${NC}"
            ;;
        3)
            echo -e "${GREEN}[+] Installing qutebrowser...${NC}"
            sudo xbps-install -y qutebrowser || echo -e "${RED}[-] Failed to install qutebrowser${NC}"
            ;;
        *)
            echo -e "${RED}[-] Invalid choice, enter [1|2|3]${NC}"
            ;;
    esac
}

next_script() {
	source checkup.sh
}

main() {
    echo -e "${GREEN}[+] Starting NullDE browser installation for${NC}"
    
    install_packages
    select_browser

    echo -e "${GREEN}[+] Installation complete!${NC}"
}

main
