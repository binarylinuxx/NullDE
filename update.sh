#!/bin/bash

confirm_install() {
    echo -e "${BLUE}Hello $USER ${CYAN} NullDE project heavily changed add eww widgets so they completly replaced waybar and a few other tool${NC}"
    echo -ne "${YELLOW}Proceed with installation? choice no if you want stay on this configuration but no more maintainable [Y/n] ${NC}"
    read -r answer

    case "$answer" in
        [Yy]|"")
            echo -e "${GREEN}[+] Starting installation...${NC}"
            pull_latest_changes
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

pull_latest_changes() {
	git pull || echo "nothing to update all actual."
}

next_script() {
	source install_pkgs.sh
}

main() {
	confirm_install
	pull
	next_script
}

main
