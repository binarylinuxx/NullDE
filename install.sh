#!/bin/bash

DIR_TO_CLONE_THE_REPO="$HOME/.dots"
NULLDE_REPO="https://github.com/binarylinuxx/NullDE.git"
REPO_NAME="NullDE"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ask_user_confirmation() {
    echo -e "${BLUE}Hello $USER! and welcome to ${CYAN}NullDE Dotfiles Hyprland installer${NC}"
    echo -ne "${YELLOW}Do you want to proceed? [Yy/Nn]${NC} "
    read -r answer

    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}[+] Cloning repo.${NC}"
        clone_repo
    elif [[ "$answer" =~ ^[Nn]$ ]]; then
        echo -e "${RED}[-] Alright Aborting.${NC}"
        exit 130
    else
        echo -e "${CYAN}[!] Failed to parse your choice${NC}"
        echo -e "${CYAN}[!] Please enter Yy/Nn ${NC}"
        ask_user_confirmation
    fi
}

clone_repo() {
    echo -e "${CYAN}[!] Creating directory...${NC}"
    mkdir -p "$DIR_TO_CLONE_THE_REPO"

    echo -e "${GREEN}[+] Created succsefully.${NC}"
    echo -e "${CYAN}[+] Cloning repository...${NC}"
    git clone "$NULLDE_REPO" "$DIR_TO_CLONE_THE_REPO"
}

enter_repository_dir() {
    echo -e "${CYAN}[+] Entering repository directory...${NC}"
    cd "$DIR_TO_CLONE_THE_REPO/$REPO_NAME" || {
        echo -e "${RED}[-] Failed to enter directory!${NC}"
        exit 1
    }

    echo -e "${GREEN}[+] Sourcing install_pkgs.sh...${NC}"
    source install_pkgs.sh
}

install_git() {
	sudo xbps-install -Syu git
}

main() {
    ask_user_confirmation
    clone_repo
    enter_repository_dir
}

main
