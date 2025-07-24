#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Проверка пакетов через xbps-query
check_packages() {
    local -a packages=(
        pulseaudio pulseaudio-devel hyprlock nerd-fonts-symbols-ttf
        gtk4-layer-shell gtk4-layer-shell-devel hyprland
        xdg-desktop-portal-hyprland rofi waybar swaybg kitty
        libadwaita hyprpaper wlogout fish-shell gtk+3-devel gtk+3 gtk4-devel gtk4
    )

    echo -e "${CYAN}[!] Checking installed packages...${NC}"
    
    local missing_count=0
    for pkg in "${packages[@]}"; do
        if xbps-query "$pkg" >/dev/null 2>&1; then
            echo -e "${GREEN}[+] $pkg installed${NC}"
        else
            echo -e "${RED}[-] $pkg NOT installed${NC}"
            ((missing_count++))
        fi
    done
    
    if [ $missing_count -gt 0 ]; then
        echo -e "${YELLOW}[!] $missing_count packages are missing${NC}"
    fi
}

# Проверка сервисов
check_services() {
    local -a services=("dbus" "seatd" "elogind")
    
    echo -e "${CYAN}[!] Checking enabled services...${NC}"
    
    for svc in "${services[@]}"; do
        if [ -d "/var/service/$svc" ]; then
            echo -e "${GREEN}[+] $svc service enabled${NC}"
        else
            echo -e "${RED}[-] $svc service NOT enabled${NC}"
        fi
    done
}

# Проверка зависимостей Hyprland
check_hyprland_deps() {
    echo -e "${CYAN}[!] Checking Hyprland dependencies...${NC}"
    
    local -a deps=(
        libinput mesa-dri wayland-protocols xorg-server-xwayland
        xdg-utils xdg-user-dirs polkit
    )
    
    for dep in "${deps[@]}"; do
        if xbps-query "$dep" >/dev/null 2>&1; then
            echo -e "${GREEN}[+] $dep installed${NC}"
        else
            echo -e "${YELLOW}[!] $dep recommended but missing${NC}"
        fi
    done
}

ask_user_reboot_confirmation() {
    echo -e "${BLUE}Dotfiles installation finished! Would you like to reboot now?${NC}"
    echo -e "${YELLOW}(Reboot is recommended to apply all changes)${NC}"
    echo -ne "${YELLOW}Do you want to proceed? [Yy/Nn]${NC} "
    read -r answer

    case "$answer" in
        [Yy]*) 
            echo -e "${GREEN}[+] Rebooting now...${NC}"
            # ИСПРАВЛЕНО: используем более совместимую команду
            sudo reboot || loginctl reboot
            ;;
        [Nn]*) 
            echo -e "${YELLOW}[!] Reboot cancelled. Please reboot manually later.${NC}"
            exit 0
            ;;
        *) 
            echo -e "${CYAN}[!] Invalid input. Please enter Yy/Nn${NC}"
            ask_user_reboot_confirmation
            ;;
    esac
}

copy_configs() {
    echo -e "${CYAN}[!] Copying config files...${NC}"
    if [ -d ".config" ]; then
        cp -r .config/ ~/ && \
        echo -e "${GREEN}[+] Configs copied successfully${NC}" || \
        echo -e "${RED}[-] Failed to copy configs${NC}"
    else
        echo -e "${YELLOW}[!] No .config directory found in current directory${NC}"
        echo -e "${YELLOW}[!] Current directory: $(pwd)${NC}"
    fi
}

main() {
    check_packages
    echo
    check_services
    echo
    check_hyprland_deps
    echo
    copy_configs
    ask_user_reboot_confirmation
}

main
