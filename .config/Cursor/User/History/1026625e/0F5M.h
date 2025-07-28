#pragma once
#include <iostream>
#include <vector>
#include <string>

// Send OSC escape sequence to set a palette color
inline void set_osc_color(int idx, const std::string& hex) {
    std::cout << "\033]4;" << idx << ";" << hex << "\007";
}
// Send OSC escape sequence to set foreground color
inline void set_osc_fg(const std::string& hex) {
    std::cout << "\033]10;" << hex << "\007";
}
// Send OSC escape sequence to set background color
inline void set_osc_bg(const std::string& hex) {
    std::cout << "\033]11;" << hex << "\007";
}

// Apply a 16-color palette and fg/bg to the terminal using OSC sequences
inline void hot_reload_terminal(const std::vector<std::string>& palette, const std::string& fg, const std::string& bg) {
    for (int i = 0; i < 16 && i < palette.size(); ++i) {
        set_osc_color(i, palette[i]);
    }
    set_osc_fg(fg);
    set_osc_bg(bg);
    std::cout.flush();
} 