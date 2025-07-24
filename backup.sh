RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

items_to_find=(".bashrc" ".zshrc" ".config")
backup_dir="$HOME/.backup"

found_items=()

check_shell_and_dot_config() {
    for item in "${items_to_find[@]}"; do
        if [ -e "$HOME/$item" ]; then
            found_items+=("$item")
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
    # ИСПРАВЛЕНО: проверяем тот файл, который подключаем
    if [ -f "checksvs.sh" ]; then
        source checksvs.sh
    else
        echo -e "${YELLOW}[!] checksvs.sh not found.${NC}"
        exit 1
    fi
}

main() {
    check_shell_and_dot_config
    next_script
}

main
