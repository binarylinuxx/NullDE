#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

setup_jetbrains_font() {
    echo -e "${CYAN}[+] Setting up JetBrains font...${NC}"
    
    # Создаем временную директорию
    local temp_dir=$(mktemp -d)
    cd "$temp_dir" || {
        echo -e "${RED}[-] Failed to create temp directory${NC}"
        return 1
    }
    
    # Скачиваем шрифт
    wget https://download-cdn.jetbrains.com/fonts/JetBrainsMono-2.304.zip || {
        echo -e "${RED}[-] Failed to download JetBrains font${NC}"
        cd - >/dev/null
        rm -rf "$temp_dir"
        return 1
    }
    
    # ИСПРАВЛЕНО: правильные флаги для unzip
    sudo mkdir -p /usr/share/fonts/jetbrains
    sudo unzip -q JetBrainsMono-2.304.zip -d /usr/share/fonts/jetbrains || {
        echo -e "${RED}[-] Failed to extract font${NC}"
        cd - >/dev/null
        rm -rf "$temp_dir"
        return 1
    }
    
    # Обновляем кэш шрифтов
    fc-cache -fv >/dev/null
    
    # Убираем временные файлы
    cd - >/dev/null
    rm -rf "$temp_dir"
    
    echo -e "${GREEN}[+] JetBrains font installed successfully${NC}"
}

setup_fish() {
    echo -e "${CYAN}[+] Setting up fish shell...${NC}"
    
    # Проверяем, установлен ли fish
    if ! command -v fish >/dev/null 2>&1; then
        echo -e "${RED}[-] Fish shell not found. Please install it first.${NC}"
        return 1
    fi
    
    # Смена shell на fish
    echo -e "${YELLOW}[!] Changing default shell to fish...${NC}"
    chsh -s /usr/bin/fish || {
        echo -e "${RED}[-] Failed to change shell to fish${NC}"
        return 1
    }
    
    echo -e "${CYAN}[+] Installing fisher (fish plugin manager)...${NC}"
    # ИСПРАВЛЕНО: выполняем команды fish в отдельной сессии
    fish -c "curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source; and fisher install jorgebucaran/fisher" || {
        echo -e "${RED}[-] Failed to install fisher${NC}"
        return 1
    }
    
    echo -e "${CYAN}[+] Installing tide theme...${NC}"
    fish -c "fisher install IlanCosman/tide@v6" || {
        echo -e "${RED}[-] Failed to install tide theme${NC}"
        return 1
    }
    
    echo -e "${GREEN}[+] Fish shell configured successfully!${NC}"
    echo -e "${YELLOW}[!] Please restart your terminal or run 'exec fish' to apply changes.${NC}"
    echo -e "${YELLOW}[!] Run 'tide configure' to setup your theme.${NC}"
}

next_script() {
    if [ -f "choice_browser.sh" ]; then
        source choice_browser.sh
    else
        echo -e "${YELLOW}[!] choice_browser.sh not found.${NC}"
        exit 1
    fi
}

main() {
    setup_jetbrains_font
    setup_fish
    next_script  # ДОБАВЛЕНО: вызов следующего скрипта
}

main
