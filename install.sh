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
    echo -e "${CYAN}[!] Creating directory...${NC}"
    mkdir -p "$DIR_TO_CLONE_THE_REPO" || {
        echo -e "${RED}[-] Failed to create directory${NC}"
        exit 1
    }

    echo -e "${GREEN}[+] Directory created successfully.${NC}"
    echo -e "${CYAN}[+] Cloning repository...${NC}"
    
    git clone "$NULLDE_REPO" "$DIR_TO_CLONE_THE_REPO/$REPO_NAME" || {
        echo -e "${RED}[-] Failed to clone repository${NC}"
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
