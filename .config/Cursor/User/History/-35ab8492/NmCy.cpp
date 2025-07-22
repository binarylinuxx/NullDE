#include <wayland-client.h>
#include <INIReader.h>
#include <iostream>

int main() {
    // Load config
    INIReader reader("config.ini");
    if (reader.ParseError() < 0) {
        std::cerr << "Can't load config.ini\n";
        return 1;
    }
    std::cout << "Config loaded. Example value: " << reader.Get("core", "example", "default") << std::endl;

    // Connect to Wayland display
    wl_display* display = wl_display_connect(nullptr);
    if (!display) {
        std::cerr << "Failed to connect to Wayland display\n";
        return 1;
    }
    std::cout << "Connected to Wayland display." << std::endl;
    wl_display_disconnect(display);
    return 0;
} 