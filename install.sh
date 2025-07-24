#!/bin/bash

DIR_TO_CLONE_THE_REPO="$HOME/.dots"
NULLDE_REPO="https://github.com/binarylinuxx/NullDE.git"
REPO_NAME="NullDE"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

ask_user_confirmation() {
    echo -e "${BLUE}Hello $USER! Welcome to ${CYAN}NullDE Dotfiles Hyprland installer${NC}"
    echo -ne "${YELLOW}Do you want to proceed? [Yy/Nn]${NC} "
    read -r answer

    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}[+] Starting installation...${NC}"
        clone_repo
    elif [[ "$answer" =~ ^[Nn]$ ]]; then
        echo -e "${RED}[-] Installation aborted.${NC}"
        exit 130
    else
        echo -e "${CYAN}[!] Failed to parse your choice${NC}"
        echo -e "${CYAN}[!] Please enter Yy/Nn${NC}"
        ask_user_confirmation
    fi
}

clone_repo() {
    echo -e "${CYAN}[!] Preparing installation directory...${NC}"
    
    # Полный путь к папке репозитория
    FULL_REPO_PATH="$DIR_TO_CLONE_THE_REPO/$REPO_NAME"
    
    # Если папка уже существует, предложить варианты
    if [ -d "$FULL_REPO_PATH" ]; then
        echo -e "${YELLOW}[!] Directory $FULL_REPO_PATH already exists.${NC}"
        echo -e "${CYAN}Choose action:${NC}"
        echo -e "${YELLOW}[1] Remove and clone fresh${NC}"
        echo -e "${YELLOW}[2] Update existing (git pull)${NC}"
        echo -e "${YELLOW}[3] Abort installation${NC}"
        echo -ne "${YELLOW}Select [1-3]: ${NC}"
        
        read -r choice
        case $choice in
            1)
                echo -e "${CYAN}[+] Removing old directory...${NC}"
                rm -rf "$FULL_REPO_PATH" || {
                    echo -e "${RED}[-] Failed to remove directory${NC}"
                    exit 1
                }
                ;;
            2)
                echo -e "${CYAN}[+] Updating existing repository...${NC}"
                cd "$FULL_REPO_PATH" || {
                    echo -e "${RED}[-] Failed to enter directory${NC}"
                    exit 1
                }
                git pull origin main || {
                    echo -e "${RED}[-] Failed to update repository${NC}"
                    exit 1
                }
                echo -e "${GREEN}[+] Repository updated successfully${NC}"
                return 0
                ;;
            3)
                echo -e "${RED}[-] Installation aborted by user${NC}"
                exit 130
                ;;
            *)
                echo -e "${RED}[-] Invalid choice${NC}"
                exit 1
                ;;
        esac
    fi
    
    # Создаем базовую директорию
    mkdir -p "$DIR_TO_CLONE_THE_REPO" || {
        echo -e "${RED}[-] Failed to create directory${NC}"
        exit 1
    }

    echo -e "${GREEN}[+] Directory prepared successfully.${NC}"
    echo -e "${CYAN}[+] Cloning repository...${NC}"
    
    git clone "$NULLDE_REPO" "$FULL_REPO_PATH" || {
        echo -e "${RED}[-] Failed to clone repository${NC}"
        echo -e "${YELLOW}[!] Check your internet connection and try again${NC}"
        exit 1
    }
    
    echo -e "${GREEN}[+] Repository cloned successfully${NC}"
}

enter_repository_dir() {
    echo -e "${CYAN}[+] Entering repository directory...${NC}"
    cd "$DIR_TO_CLONE_THE_REPO/$REPO_NAME" || {
        echo -e "${RED}[-] Failed to enter directory!${NC}"
        exit 1
    }

    echo -e "${GREEN}[+] Starting package installation...${NC}"
    if [ -f "install_pkgs.sh" ]; then
        source install_pkgs.sh
    else
        echo -e "${RED}[-] install_pkgs.sh not found!${NC}"
        exit 1
    fi
}

install_git() {
    echo -e "${CYAN}[+] Installing git...${NC}"
    sudo xbps-install -Syu git || {
        echo -e "${RED}[-] Failed to install git${NC}"
        exit 1
    }
}

main() {
    # Проверяем наличие git
    if ! command -v git >/dev/null 2>&1; then
        install_git
    fi
    
    ask_user_confirmation
    clone_repo
    enter_repository_dir
}

main
