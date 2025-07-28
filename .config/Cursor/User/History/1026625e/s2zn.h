#pragma once
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include <unistd.h>

// Try to detect and reload color schemes for common Linux desktop environments and compositors
inline void hot_reload_apply() {
    // Check for Sway
    if (getenv("SWAYSOCK")) {
        std::cout << "[hot_reload] Reloading Sway config..." << std::endl;
        system("swaymsg reload");
        system("swaymsg exec 'pkill -SIGUSR2 waybar'"); // reload waybar if running
        return;
    }
    // Check for Hyprland
    if (getenv("HYPRLAND_INSTANCE_SIGNATURE")) {
        std::cout << "[hot_reload] Reloading Hyprland config..." << std::endl;
        system("killall -SIGUSR2 waybar 2>/dev/null");
        system("killall -SIGUSR2 hyprpaper 2>/dev/null");
        system("hyprctl reload");
        return;
    }
    // Check for GNOME
    if (getenv("XDG_CURRENT_DESKTOP") && std::string(getenv("XDG_CURRENT_DESKTOP")).find("GNOME") != std::string::npos) {
        std::cout << "[hot_reload] Reloading GNOME shell theme..." << std::endl;
        system("gsettings set org.gnome.desktop.interface gtk-theme $(gsettings get org.gnome.desktop.interface gtk-theme)");
        system("gsettings set org.gnome.desktop.interface icon-theme $(gsettings get org.gnome.desktop.interface icon-theme)");
        return;
    }
    // Check for KDE
    if (getenv("XDG_CURRENT_DESKTOP") && std::string(getenv("XDG_CURRENT_DESKTOP")).find("KDE") != std::string::npos) {
        std::cout << "[hot_reload] Reloading KDE color scheme..." << std::endl;
        system("qdbus org.kde.KWin /KWin reconfigure");
        system("lookandfeeltool -a $(lookandfeeltool -l | head -n1)");
        return;
    }
    // Fallback: try to reload waybar if running
    std::cout << "[hot_reload] Attempting to reload waybar..." << std::endl;
    system("pkill -SIGUSR2 waybar 2>/dev/null");
    std::cout << "[hot_reload] No known desktop environment detected or no reload action taken." << std::endl;
}

/*
Supported environments:
- Sway: reloads config and signals waybar
- Hyprland: reloads hyprctl, signals waybar and hyprpaper
- GNOME: triggers GTK and icon theme reload
- KDE: triggers KWin and look-and-feel reload
- Fallback: signals waybar if running
*/
