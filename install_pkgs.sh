#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Some Depends
MAIN_PACKAGES="unzip wget libinput mesa-dri wayland-protocols xorg-server-xwayland xdg-utils xdg-user-dirs polkit"
# For Hyprland
HYPRLAND_PACKAGES="pulseaudio pulseaudio-devel hyprlock nerd-fonts-symbols-ttf gtk4-layer-shell gtk4-layer-shell-devel hyprland xdg-desktop-portal-hyprland"
# Look 
UI_PACKAGES="rofi Waybar swaybg kitty libadwaita hyprpaper wlogout fish-shell gtk4-devel gtk4 gtk+3-devel gtk+3"

# ИСПРАВЛЕНО: используем абсолютный путь
BIN_DIR="$(pwd)/BIN"

plug_repo() {
    echo -e "${CYAN}[!] Adding Hyprland repository...${NC}"
    echo 'repository=https://raw.githubusercontent.com/Makrennel/hyprland-void/repository-x86_64-glibc' | sudo tee /etc/xbps.d/hyprland-void.conf > /dev/null
    
    # Обновляем после добавления репозитория
    sudo xbps-install -S || {
        echo -e "${RED}[-] Failed to sync with new repository${NC}"
        return 1
    }
    
    echo -e "${GREEN}[+] Repository added successfully${NC}"
}

install_pkgs() {
    echo -e "${CYAN}[!] Installing dependencies, please be patient...${NC}"
    
    # Установка основных пакетов
    echo -e "${CYAN}[+] Installing main packages...${NC}"
    sudo xbps-install -y $MAIN_PACKAGES || {
        echo -e "${RED}[-] Failed to install main packages${NC}"
        return 1
    }
    
    echo -e "${CYAN}[+] Installing Hyprland packages...${NC}"
    sudo xbps-install -y $HYPRLAND_PACKAGES || {
        echo -e "${RED}[-] Failed to install Hyprland packages${NC}"
        return 1
    }
    
    echo -e "${CYAN}[+] Installing UI packages...${NC}"
    sudo xbps-install -y $UI_PACKAGES || {
        echo -e "${RED}[-] Failed to install UI packages${NC}"
        return 1
    }
    
    # ИСПРАВЛЕНО: проверяем существование BIN директории
    if [ -d "$BIN_DIR" ]; then
        echo -e "${CYAN}[+] Installing binary packages from local repository...${NC}"
        sudo xbps-install -R "$BIN_DIR" matugen hyprsettings || {
            echo -e "${YELLOW}[!] Failed to install some binary packages (non-critical)${NC}"
        }
    else
        echo -e "${YELLOW}[!] BIN directory not found at $BIN_DIR, skipping binary packages${NC}"
    fi
    
    echo -e "${GREEN}[+] Package installation completed${NC}"
}

next_script() {
    if [ -f "backup.sh" ]; then
        source backup.sh
    else
        echo -e "${YELLOW}[!] backup.sh not found.${NC}"
        exit 1
    fi
}

main() {
    plug_repo || {
        echo -e "${RED}[-] Failed to setup repository${NC}"
        exit 1
    }
    
    install_pkgs || {
        echo -e "${RED}[-] Package installation failed${NC}"
        exit 1
    }
    
    next_script
}

main
