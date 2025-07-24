#!/bin/bash

setup_jetbrains_font() {
	wget https://download-cdn.jetbrains.com/fonts/JetBrainsMono-2.304.zip
	sudo unzip JetBrainsMono-2.304.zip -D /usr/share/fonts
	fc-cache -fv
}

setup_fish() {
	chsh -s /usr/bin/fish
	#get fisher and plugings
	echo -e "[!] installing fisher - fish plugin MGR"
	curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
	echo -e "[!] Follow steps that now tide fish theme setup guide you."
	fisher install IlanCosman/tide@v6
}

main() {
	setup_jetbrains_font
	setup_fish
}
