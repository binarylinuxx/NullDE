#!/bin/bash

# Configuration
REPO_DIR="$HOME/.dots"           # Only clone into ~/.dots/NullDE (not ~/.dots/NullDE/NullDE)
REPO_URL="https://github.com/binarylinuxx/NullDE.git"
REPO_NAME="NullDE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Functions ---

# Ask for user confirmation
confirm_install() {
    echo -e "${BLUE}Welcome to ${CYAN}NullDE Dotfiles Installer${NC}"
    echo -ne "${YELLOW}Proceed with installation? [Y/n] ${NC}"
    read -r answer

    case "$answer" in
        [Yy]|"") 
            echo -e "${GREEN}[+] Starting installation...${NC}"
            ;;
        [Nn])
            echo -e "${RED}[-] Installation aborted.${NC}"
            exit 1
            ;;
        *)
            echo -e "${RED}[!] Invalid choice. Please enter Y/n.${NC}"
            confirm_install
            ;;
    esac
}

# Install Git if missing
install_git() {
    if ! command -v git &> /dev/null; then
        echo -e "${CYAN}[+] Installing Git...${NC}"
        sudo xbps-install -Sy git || {
            echo -e "${RED}[-] Failed to install Git!${NC}"
            exit 1
        }
    fi
}

# Clone or update the repository
setup_repo() {
    echo -e "${CYAN}[+] Setting up repository...${NC}"

    # If folder exists, ask what to do
    if [ -d "$REPO_DIR/$REPO_NAME" ]; then
        echo -e "${YELLOW}[!] '$REPO_DIR/$REPO_NAME' already exists!${NC}"
        echo -e "${CYAN}Choose an option:${NC}"
        echo -e "  ${YELLOW}1) Delete and re-clone (clean install)${NC}"
        echo -e "  ${YELLOW}2) Update existing (git pull)${NC}"
        echo -e "  ${YELLOW}3) Abort${NC}"
        echo -ne "${YELLOW}Select [1-3]: ${NC}"
        read -r choice

        case "$choice" in
            1)
                echo -e "${CYAN}[+] Removing old repository...${NC}"
                rm -rf "$REPO_DIR/$REPO_NAME" || {
                    echo -e "${RED}[-] Failed to delete folder!${NC}"
                    exit 1
                }
                ;;
            2)
                echo -e "${CYAN}[+] Updating repository...${NC}"
                cd "$REPO_DIR/$REPO_NAME" || exit 1
                git pull || {
                    echo -e "${RED}[-] Failed to update!${NC}"
                    exit 1
                }
                echo -e "${GREEN}[+] Successfully updated.${NC}"
                return 0
                ;;
            3)
                echo -e "${RED}[-] Aborted by user.${NC}"
                exit 1
                ;;
            *)
                echo -e "${RED}[-] Invalid choice!${NC}"
                exit 1
                ;;
        esac
    fi

    # Clone the repo
    echo -e "${CYAN}[+] Cloning repository...${NC}"
    mkdir -p "$REPO_DIR" || exit 1
    git clone "$REPO_URL" "$REPO_DIR/$REPO_NAME" || {
        echo -e "${RED}[-] Clone failed! Check internet.${NC}"
        exit 1
    }
    echo -e "${GREEN}[+] Repository cloned successfully.${NC}"
}

# Run the installer script
run_installer() {
    echo -e "${CYAN}[+] Running installer...${NC}"
    cd "$REPO_DIR/$REPO_NAME" || {
        echo -e "${RED}[-] Failed to enter directory!${NC}"
        exit 1
    }

    if [ -f "install_pkgs.sh" ]; then
        ./install_pkgs.sh
    else
        echo -e "${RED}[-] 'install_pkgs.sh' not found!${NC}"
        exit 1
    fi
}

# --- Main ---
main() {
    install_git          # Ensure Git is installed
    confirm_install     # Ask for confirmation
    setup_repo          # Clone/update repo
    run_installer       # Run the package installer
}

main
