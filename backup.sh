#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

items_to_find=(".bashrc" ".zshrc" ".config")
backup_dir="$HOME/.backup"  # Исправлено: ~ не раскрывается в кавычках

found_items=()  # Массив для хранения найденных файлов/папок

check_shell_and_dot_config() {
    for item in "${items_to_find[@]}"; do
        if [ -e "$HOME/$item" ]; then
            found_items+=("$item")  # Добавляем в массив найденных
        fi
    done

    if [ ${#found_items[@]} -eq 0 ]; then
        echo -e "${YELLOW}[!] No files/folders found to backup.${NC}"
        exit 0
    else
        echo -e "${BLUE}Found files/folders: ${found_items[*]}. Backup them?${NC}"
        ask_user_confirmation
    fi
}

ask_user_confirmation() {
    echo -ne "${YELLOW}Proceed? [Yy/Nn]${NC} "
    read -r answer

    case "$answer" in
        [Yy]*) 
            echo -e "${GREEN}[+] Starting backup...${NC}"
            backuping
            ;;
        [Nn]*) 
            echo -e "${RED}[-] Aborted.${NC}"
            exit 130
            ;;
        *) 
            echo -e "${CYAN}[!] Invalid input. Use Yy/Nn.${NC}"
            ask_user_confirmation
            ;;
    esac
}

backuping() {
    mkdir -p "$backup_dir" || {
        echo -e "${RED}[-] Failed to create $backup_dir.${NC}"
        exit 1
    }

    for item in "${found_items[@]}"; do
        cp -r "$HOME/$item" "$backup_dir/" && \
        echo -e "${GREEN}[+] Copied: $item → $backup_dir/${NC}" || \
        echo -e "${RED}[-] Failed to copy: $item${NC}"
    done
}

next_script() {
    if [ -f "cope_and_setup_dotfiles.sh" ]; then
        source checksvs.sh
    else
        echo -e "${YELLOW}[!] Next script not found.${NC}"
    fi
}

main() {
    check_shell_and_dot_config
    next_script
}

main
