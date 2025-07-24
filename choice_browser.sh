#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# УДАЛЕНО: ненужная проверка root (используем sudo)

# Установка базовых пакетов
install_base_packages() {
    echo -e "${CYAN}[+] Updating package database...${NC}"
    sudo xbps-install -Sy || {
        echo -e "${RED}[-] Failed to update packages${NC}"
        return 1
    }

    echo -e "${CYAN}[+] Installing base packages...${NC}"
    sudo xbps-install -y git make gcc pkg-config || {
        echo -e "${RED}[-] Failed to install base packages${NC}"
        return 1
    }
}

# Выбор браузера
select_browser() {
    echo -e "${CYAN}[!] Choose browser to install:${NC}"
    echo -e "${YELLOW}[1] Firefox${NC}"
    echo -e "${YELLOW}[2] Chromium${NC}"
    echo -e "${YELLOW}[3] qutebrowser (minimal)${NC}"
    echo -e "${YELLOW}[4] Skip browser installation${NC}"
    echo -ne "${YELLOW}Select [1-4]: ${NC}"

    read -r choice
    case $choice in
        1)
            echo -e "${GREEN}[+] Installing Firefox...${NC}"
            sudo xbps-install -y firefox && \
            echo -e "${GREEN}[+] Firefox installed successfully${NC}" || \
            echo -e "${RED}[-] Failed to install Firefox${NC}"
            ;;
        2)
            echo -e "${GREEN}[+] Installing Chromium...${NC}"
            sudo xbps-install -y chromium && \
            echo -e "${GREEN}[+] Chromium installed successfully${NC}" || \
            echo -e "${RED}[-] Failed to install Chromium${NC}"
            ;;
        3)
            echo -e "${GREEN}[+] Installing qutebrowser...${NC}"
            sudo xbps-install -y qutebrowser && \
            echo -e "${GREEN}[+] qutebrowser installed successfully${NC}" || \
            echo -e "${RED}[-] Failed to install qutebrowser${NC}"
            ;;
        4)
            echo -e "${YELLOW}[!] Skipping browser installation${NC}"
            ;;
        *)
            echo -e "${RED}[-] Invalid choice. Please enter 1, 2, 3, or 4${NC}"
            select_browser  # Рекурсивный вызов при неверном выборе
            ;;
    esac
}

next_script() {
    if [ -f "checkup.sh" ]; then
        source checkup.sh
    else
        echo -e "${YELLOW}[!] checkup.sh not found.${NC}"
        exit 1
    fi
}

main() {
    echo -e "${GREEN}[+] Starting NullDE browser installation${NC}"
    
    install_base_packages || {
        echo -e "${RED}[-] Failed to install base packages${NC}"
        exit 1
    }
    
    select_browser
    next_script

    echo -e "${GREEN}[+] Browser installation complete!${NC}"
}

main
