#pragma once
#include <fstream>
#include <iostream>
#include <string>
#include <cstdlib>
#include <map>

// Helper: Send OSC escape sequence to kitty
inline void send_kitty_osc(const std::string& osc) {
    std::cout << "\033]" << osc << "\007";
    std::cout.flush();
}

// Parse a simple key value config (kitty-colors.conf)
inline std::map<std::string, std::string> parse_kitty_conf(const std::string& path) {
    std::map<std::string, std::string> colors;
    std::ifstream file(path);
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') continue;
        size_t pos = line.find_first_of(" \	");
        if (pos == std::string::npos) continue;
        std::string key = line.substr(0, pos);
        std::string value = line.substr(pos);
        value.erase(0, value.find_first_not_of(" \	"));
        colors[key] = value;
    }
    return colors;
}

// Hot reload colors in kitty terminal
inline void hot_reload_kitty(const std::string& kitty_conf_path = "kitty-colors.conf") {
    // Only apply if running inside kitty
    const char* term = getenv("TERM");
    if (!term || std::string(term).find("kitty") == std::string::npos) {
        return;
    }
    auto colors = parse_kitty_conf(kitty_conf_path);
    // Map kitty color names to OSC codes
    std::map<std::string, int> color_indices = {
        {"color0", 0}, {"color1", 1}, {"color2", 2}, {"color3", 3},
        {"color4", 4}, {"color5", 5}, {"color6", 6}, {"color7", 7},
        {"color8", 8}, {"color9", 9}, {"color10", 10}, {"color11", 11},
        {"color12", 12}, {"color13", 13}, {"color14", 14}, {"color15", 15}
    };
    // Set basic 16 colors
    for (const auto& [name, idx] : color_indices) {
        auto it = colors.find(name);
        if (it != colors.end()) {
            send_kitty_osc("4;" + std::to_string(idx) + ";" + it->second);
        }
    }
    // Set foreground/background if present
    if (colors.count("foreground")) {
        send_kitty_osc("10;" + colors["foreground"]);
    }
    if (colors.count("background")) {
        send_kitty_osc("11;" + colors["background"]);
    }
    if (colors.count("selection_foreground")) {
        send_kitty_osc("17;" + colors["selection_foreground"]);
    }
    if (colors.count("selection_background")) {
        send_kitty_osc("19;" + colors["selection_background"]);
    }
}
