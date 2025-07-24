#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

TO_INSTALL="libinput mesa-dri wayland-protocols xorg-server-xwayland xdg-utils xdg-user-dirs polkit pulseaudio pulseaudio-devel hyprlock nerd-fonts-symbols-ttf gtk4-layer-shell gtk4-layer-shell-devel hyprland xdg-desktop-portal-hyprland rofi Waybar swaybg kitty libadwita hyprpaper wlogout fish-shell gtk4-devel gtk4 gtk3"
BIN_DIR="BIN/"

plug_repo() {
	echo -e "${CYAN}[!] Script gonna plug a repository"
	echo repository=https://raw.githubusercontent.com/Makrennel/hyprland-void/repository-x86_64-glibc | sudo tee /etc/xbps.d/hyprland-void.conf
}

install_pkgs() {
	echo -e "${CYAN}[!] Install depends, be pateint might would be long depending on your internet."
	#Install Oficcialy Avilable
	sudo xbps-install -Syu "$TO_INSTALL"
	#Install Binary's
	sudo xbps-install -R "$BIN_DIR" matugen hyprsettings
}

next_script() {
	source ./backup.sh
}

main() {
	plug_repo
	install_pkgs
	next_script
}
