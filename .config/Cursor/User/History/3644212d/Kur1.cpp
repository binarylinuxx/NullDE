#include "hot_reload.h"
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <regex>
#include <filesystem>
#include <cstdlib>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cmath>

namespace fs = std::filesystem;

struct Color {
    int r, g, b;
    
    Color(int red = 0, int green = 0, int blue = 0) : r(red), g(green), b(blue) {}
    
    std::string toHex() const {
        std::stringstream ss;
        ss << "#" << std::hex << std::setfill('0') 
           << std::setw(2) << r 
           << std::setw(2) << g 
           << std::setw(2) << b;
        return ss.str();
    }

    void display() const {
        std::cout << "\033[48;2;" << r << ";" << g << ";" << b << "m     \033[0m "
                  << "RGB: " << std::setw(3) << r << ", " << std::setw(3) << g << ", " << std::setw(3) << b
                  << "  HEX: " << toHex()
                  << "  HSV: " << toHsv() << "\n";
    }
    
    std::string toRgb() const {
        return "rgb(" + std::to_string(r) + ", " + std::to_string(g) + ", " + std::to_string(b) + ")";
    }
    
    std::string toRgba() const {
        return "rgba(" + std::to_string(r) + ", " + std::to_string(g) + ", " + std::to_string(b) + ", 1.0)";
    }
    
    std::string toHsv() const {
        double red = r / 255.0;
        double green = g / 255.0;
        double blue = b / 255.0;
        
        double max = std::max({red, green, blue});
        double min = std::min({red, green, blue});
        double delta = max - min;
        
        double h = 0, s = 0, v = max;
        
        if (delta != 0) {
            s = delta / max;
            if (max == red) {
                h = 60 * (fmod((green - blue) / delta, 6));
            } else if (max == green) {
                h = 60 * ((blue - red) / delta + 2);
            } else {
                h = 60 * ((red - green) / delta + 4);
            }
        }
        
        if (h < 0) h += 360;
        
        return "hsv(" + std::to_string((int)h) + ", " + 
               std::to_string((int)(s * 100)) + "%, " + 
               std::to_string((int)(v * 100)) + "%)";
    }
    
    Color decreaseBrightness(double factor) const {
        int newR = std::max(0, (int)(r * (1.0 - factor)));
        int newG = std::max(0, (int)(g * (1.0 - factor)));
        int newB = std::max(0, (int)(b * (1.0 - factor)));
        return Color(newR, newG, newB);
    }
    
    Color increaseBrightness(double factor) const {
        int newR = std::min(255, (int)(r * (1.0 + factor)));
        int newG = std::min(255, (int)(g * (1.0 + factor)));
        int newB = std::min(255, (int)(b * (1.0 + factor)));
        return Color(newR, newG, newB);
    }

    Color desaturate(double factor) const {
        double red = r / 255.0;
        double green = g / 255.0;
        double blue = b / 255.0;
        
        double max = std::max({red, green, blue});
        double min = std::min({red, green, blue});
        double delta = max - min;
        
        double h = 0, s = 0, v = max;
        
        if (delta != 0) {
            s = delta / max;
            if (max == red) {
                h = 60 * (fmod((green - blue) / delta, 6));
            } else if (max == green) {
                h = 60 * ((blue - red) / delta + 2);
            } else {
                h = 60 * ((red - green) / delta + 4);
            }
        }
        
        if (h < 0) h += 360;
        
        s *= (1.0 - factor);
        
        double c = v * s;
        double x = c * (1 - std::abs(fmod(h / 60.0, 2) - 1));
        double m = v - c;
        
        double r_prime = 0, g_prime = 0, b_prime = 0;
        if (h >= 0 && h < 60) {
            r_prime = c;
            g_prime = x;
            b_prime = 0;
        } else if (h < 120) {
            r_prime = x;
            g_prime = c;
            b_prime = 0;
        } else if (h < 180) {
            r_prime = 0;
            g_prime = c;
            b_prime = x;
        } else if (h < 240) {
            r_prime = 0;
            g_prime = x;
            b_prime = c;
        } else if (h < 300) {
            r_prime = x;
            g_prime = 0;
            b_prime = c;
        } else {
            r_prime = c;
            g_prime = 0;
            b_prime = x;
        }
        
        int newR = std::min(255, (int)((r_prime + m) * 255));
        int newG = std::min(255, (int)((g_prime + m) * 255));
        int newB = std::min(255, (int)((b_prime + m) * 255));
        return Color(newR, newG, newB);
    }

    Color darken(double factor) const {
        double red = r / 255.0;
        double green = g / 255.0;
        double blue = b / 255.0;
        
        double max = std::max({red, green, blue});
        double v = max * (1.0 - factor);
        
        int newR = std::max(0, (int)(v * 255));
        int newG = std::max(0, (int)(v * 255));
        int newB = std::max(0, (int)(v * 255));
        return Color(newR, newG, newB);
    }
};

class ConfigParser {
private:
    std::map<std::string, std::map<std::string, std::string>> sections;

    std::string expandPath(const std::string& path) const {
        if (path.empty()) return path;

        if (path[0] == '~') {
            const char* home = getenv("HOME");
            if (home) {
                return std::string(home) + path.substr(1);
            }
        }
        return path;
    }

public:
    bool parseConfig(const std::string& filename) {
        std::string expandedFilename = expandPath(filename);
        std::ifstream file(expandedFilename);
    
        if (!file.is_open()) {
            std::cerr << "[!] Warning: Could not open config file: " << filename << std::endl;
            return false;
        }
    
        std::string line;
        std::string currentSection = "";
    
        while (std::getline(file, line)) {
            line.erase(0, line.find_first_not_of(" \t"));
            line.erase(line.find_last_not_of(" \t") + 1);
    
            if (line.empty() || line[0] == '#' || line[0] == ';' || line[0] == '!') {
                continue;
            }
    
            if (line[0] == '[' && line.back() == ']') {
                currentSection = line.substr(1, line.length() - 2);
                sections[currentSection];
                continue;
            }
    
            if (!currentSection.empty()) {
                size_t equalPos = line.find('=');
                if (equalPos != std::string::npos) {
                    std::string key = line.substr(0, equalPos);
                    std::string value = line.substr(equalPos + 1);
    
                    key.erase(0, key.find_first_not_of(" \t"));
                    key.erase(key.find_last_not_of(" \t") + 1);
                    value.erase(0, value.find_first_not_of(" \t"));
                    value.erase(value.find_last_not_of(" \t") + 1);
    
                    sections[currentSection][key] = value;
                }
            }
        }
    
        file.close();
        return true;
    }

    std::string getValue(const std::string& section, const std::string& key) const {
        auto sectionIt = sections.find(section);
        if (sectionIt != sections.end()) {
            auto keyIt = sectionIt->second.find(key);
            if (keyIt != sectionIt->second.end()) {
                return expandPath(keyIt->second);
            }
        }
        return "";
    }

    std::vector<std::string> getSections() const {
        std::vector<std::string> result;
        for (const auto& section : sections) {
            result.push_back(section.first);
        }
        return result;
    }

    bool hasSection(const std::string& section) const {
        return sections.find(section) != sections.end();
    }
};

class ColorExtractor {
public:
    static std::vector<Color> extractColors(const std::string& imagePath) {
        std::cout << "[=>] Extracting dominant colors from: " << imagePath << std::endl;
        
        // Sanitize imagePath: only allow files that exist and do not contain dangerous characters
        if (imagePath.find('"') != std::string::npos || imagePath.find(';') != std::string::npos || imagePath.find('|') != std::string::npos) {
            std::cerr << "[-] Invalid characters in image path." << std::endl;
            return generateFallbackColors();
        }
        if (!fs::exists(imagePath)) {
            std::cerr << "[-] Image file does not exist: " << imagePath << std::endl;
            return generateFallbackColors();
        }
        
        // Use unique temp file
        int pid = getpid();
        std::string tempFile = "/tmp/cppwal_colors_" + std::to_string(pid) + ".txt";
        
        std::string command = "magick \"" + imagePath + "\" -resize 200x200 +dither -colors 16 -format \"%c\" histogram:info: > " + tempFile;
        
        int result = system(command.c_str());
        if (result != 0) {
            std::cerr << "[-] Failed to extract colors using ImageMagick" << std::endl;
            return generateFallbackColors();
        }
        
        std::vector<Color> colors;
        std::ifstream file(tempFile);
        std::string line;
        
        while (std::getline(file, line) && colors.size() < 16) {
            std::regex colorRegex(R"(#([0-9A-Fa-f]{6}))");
            std::smatch match;
            
            if (std::regex_search(line, match, colorRegex)) {
                std::string hexColor = match[1].str();
                int r = std::stoi(hexColor.substr(0, 2), nullptr, 16);
                int g = std::stoi(hexColor.substr(2, 2), nullptr, 16);
                int b = std::stoi(hexColor.substr(4, 2), nullptr, 16);
                colors.emplace_back(r, g, b);
            }
        }
        
        file.close();
        fs::remove(tempFile);
        
        while (colors.size() < 16) {
            colors.push_back(generateColorVariant(colors.empty() ? Color(128, 128, 128) : colors[0], colors.size()));
        }

        std::cout << "\n[+] Extracted " << colors.size() << " colors:\n";
        for (size_t i = 0; i < colors.size(); ++i) {
            std::cout << "Color " << std::setw(2) << i << ": ";
            colors[i].display();
        }
        std::cout << std::endl;
        
        return colors;
    }
    
private:
    static std::vector<Color> generateFallbackColors() {
        std::cout << "[!] Warning: Using fallback color palette" << std::endl;
        std::vector<Color> colors = {
            Color(80, 80, 80),      // Brighter color0 for better visibility
            Color(204, 102, 102),
            Color(181, 189, 104),
            Color(240, 198, 116),
            Color(129, 162, 190),
            Color(178, 148, 187),
            Color(138, 190, 183),
            Color(197, 200, 198),
            Color(90, 90, 90),
            Color(224, 108, 117),
            Color(192, 202, 115),
            Color(249, 208, 127),
            Color(140, 173, 201),
            Color(189, 159, 198),
            Color(149, 201, 194),
            Color(220, 223, 221)
        };
        return colors;
    }
    
    static Color generateColorVariant(const Color& base, int index) {
        double factor = (index % 8) * 0.1;
        if (index < 8) {
            return base.decreaseBrightness(factor);
        } else {
            return base.increaseBrightness(factor);
        }
    }
};

class TemplateProcessor {
private:
    std::vector<Color> colors;
    
    std::string applyFilter(const Color& color, const std::string& filter) {
        std::regex filterRegex(R"((\w+)(?:_([\d.]+))?)");
        std::smatch match;
        
        if (std::regex_search(filter, match, filterRegex)) {
            std::string filterName = match[1].str();
            std::string valueStr = match[2].str();
            double value = 0.5;
            if (!valueStr.empty()) {
                try {
                    value = std::stod(valueStr) / 100.0;
                } catch (const std::exception&) {
                    value = 0.5;
                }
            }
            
            if (filterName == "decrease_brightness" || filterName == "decrease_brightnes") {
                return color.decreaseBrightness(value).toHex();
            } else if (filterName == "increase_brightness") {
                return color.increaseBrightness(value).toHex();
            } else if (filterName == "dcel") {
                return color.desaturate(value).toHex();
            } else if (filterName == "dcol") {
                return color.darken(value).toHex();
            }
        }
        
        return color.toHex();
    }
    
public:
    TemplateProcessor(const std::vector<Color>& colorPalette) : colors(colorPalette) {}
    
    bool processTemplate(const std::string& templatePath, const std::string& outputPath) {
        std::cout << "[=>] Processing template: " << templatePath << std::endl;
        
        std::ifstream templateFile(templatePath);
        if (!templateFile.is_open()) {
            std::cerr << "[-] Failed to open template file: " << templatePath << std::endl;
            return false;
        }
        
        std::string content((std::istreambuf_iterator<char>(templateFile)),
                           std::istreambuf_iterator<char>());
        templateFile.close();
        
        // Updated regex to capture fg/bg in either the index or as a type
        std::regex variableRegex(R"(\{\{color\.(\w+)\.(\w+)(?:\s*\|\s*(\w+(?:_\d+)?))?\}\})");
        std::string result = content;
        
        std::sregex_iterator iter(content.begin(), content.end(), variableRegex);
        std::sregex_iterator end;
        
        for (; iter != end; ++iter) {
            std::smatch match = *iter;
            std::string fullMatch = match[0].str();
            std::string format = match[1].str();
            std::string indexOrType = match[2].str();
            std::string filter = match[3].str();
            
            size_t colorIndex = 0;
            if (indexOrType == "fg") {
                colorIndex = 7; // Use color7 for foreground
            } else if (indexOrType == "bg") {
                colorIndex = 0; // Use color0 for background
            } else {
                try {
                    colorIndex = std::stoi(indexOrType);
                } catch (const std::exception&) {
                    colorIndex = 0;
                }
            }
            
            if (colorIndex < colors.size()) {
                std::string replacement;
                
                if (!filter.empty()) {
                    replacement = applyFilter(colors[colorIndex], filter);
                } else {
                    if (format == "hex") {
                        replacement = colors[colorIndex].toHex();
                    } else if (format == "rgb") {
                        replacement = colors[colorIndex].toRgb();
                    } else if (format == "rgba") {
                        replacement = colors[colorIndex].toRgba();
                    } else if (format == "hsv") {
                        replacement = colors[colorIndex].toHsv();
                    } else {
                        replacement = colors[colorIndex].toHex();
                    }
                }
                
                size_t pos = result.find(fullMatch);
                while (pos != std::string::npos) {
                    result.replace(pos, fullMatch.length(), replacement);
                    pos = result.find(fullMatch, pos + replacement.length());
                }
            }
        }
        
        fs::path outputDir = fs::path(outputPath).parent_path();
        if (!outputDir.empty() && !fs::exists(outputDir)) {
            fs::create_directories(outputDir);
        }
        
        std::ofstream outputFile(outputPath);
        if (!outputFile.is_open()) {
            std::cerr << "[-] Failed to create output file: " << outputPath << std::endl;
            return false;
        }
        
        outputFile << result;
        outputFile.close();
        
        std::cout << "[+] Template processed successfully: " << outputPath << std::endl;
        return true;
    }
};

class CppWal {
private:
    std::string configPath;
    ConfigParser config;
    
    void displayColors(const std::vector<Color>& colors) const {
        std::cout << "\nGenerated Color Palette:\n";
        std::cout << "┌─────────────────────┬────────────────────┐\n";
        int n = static_cast<int>(colors.size());
        for (int i = 0; i < 8 && (i + 8) < n; i++) {
            Color left = colors[i];
            std::string leftHex = left.toHex();
            std::cout << "│ \033[48;2;" << left.r << ";" << left.g << ";" << left.b << "m     \033[0m ";
            std::cout << std::left << std::setw(10) << leftHex << "    │ ";
            
            Color right = colors[i+8];
            std::string rightHex = right.toHex();
            std::cout << "\033[48;2;" << right.r << ";" << right.g << ";" << right.b << "m     \033[0m ";
            std::cout << std::left << std::setw(10) << rightHex << "   │\n";
        }
        std::cout << "└─────────────────────┴────────────────────┘\n";
    }

    bool createDefaultConfig() {
        std::cout << "[=>] Creating default configuration..." << std::endl;
        
        fs::path configDir = fs::path(configPath).parent_path();
        if (!fs::exists(configDir)) {
            fs::create_directories(configDir);
        }
        
        std::ofstream configFile(configPath);
        if (!configFile.is_open()) {
            std::cerr << "[-] Failed to create config file: " << configPath << std::endl;
            return false;
        }
        
        configFile << "[config]\n";
        configFile << "# cppwal configuration file\n\n";
        configFile << "[template.example]\n";
        configFile << "template_path = ~/.config/cppwal/waybar.css\n";
        configFile << "output_path = ~/.config/waybar/colors.css\n";
        
        configFile.close();
        
        std::string templatePath = std::string(getenv("HOME")) + "/.config/cppwal/waybar.css";
        std::ofstream templateFile(templatePath);
        if (templateFile.is_open()) {
            templateFile << "/* Generated by cppwal */\n";
            for (int i = 0; i < 16; i++) {
                templateFile << "@define-color color" << i << " {{color.hex." << i << "}};\n";
            }
            templateFile << "\n/* Example with filters */\n";
            templateFile << "@define-color background {{color.hex.bg}};\n";
            templateFile << "@define-color foreground {{color.hex.fg}};\n";
            templateFile << "@define-color desaturated {{color.hex.1 | dcel_50}};\n";
            templateFile << "@define-color darkened {{color.hex.2 | dcol_20}};\n";
            templateFile.close();
        }
        
        std::cout << "[+] Default configuration created: " << configPath << std::endl;
        std::cout << "[+] Example template created: " << templatePath << std::endl;
        
        return config.parseConfig(configPath);
    }

public:
    CppWal() {
        const char* home = getenv("HOME");
        if (home) {
            configPath = std::string(home) + "/.config/cppwal/config.ini";
        } else {
            configPath = "config.ini";
        }
    }
    
    bool initialize() {
        std::cout << "[=>] Initializing cppwal..." << std::endl;
        
        if (!fs::exists(configPath)) {
            std::cerr << "[!] Warning: Config file not found: " << configPath << std::endl;
            return createDefaultConfig();
        }
        
        if (!config.parseConfig(configPath)) {
            std::cerr << "[-] Failed to parse config file" << std::endl;
            return false;
        }
        
        if (!config.hasSection("config")) {
            std::cerr << "[-] Failed: Config file must contain [config] section" << std::endl;
            return false;
        }
        
        std::cout << "[+] Configuration loaded successfully" << std::endl;
        return true;
    }
    
    bool processImage(const std::string& imagePath) {
        if (!fs::exists(imagePath)) {
            std::cerr << "[-] Failed: Image file not found: " << imagePath << std::endl;
            return false;
        }

        std::vector<Color> colors = ColorExtractor::extractColors(imagePath);
        if (colors.empty()) {
            std::cerr << "[-] Failed to extract colors from image" << std::endl;
            return false;
        }

        displayColors(colors);

        // Apply colors to the current terminal using OSC escape sequences
        std::vector<std::string> palette;
        for (const auto& color : colors) palette.push_back(color.toHex());
        if (palette.size() >= 8) {
            hot_reload_terminal(palette, palette[7], palette[0]);
        }

        TemplateProcessor processor(colors);
        std::vector<std::string> sections = config.getSections();
        bool allSuccess = true;

        for (const std::string& section : sections) {
            if (section == "config") continue;

            std::string templatePath = config.getValue(section, "template_path");
            std::string outputPath = config.getValue(section, "output_path");

            if (templatePath.empty() || outputPath.empty()) {
                std::cerr << "[!] Warning: Incomplete configuration for section: " << section << std::endl;
                continue;
            }

            if (!processor.processTemplate(templatePath, outputPath)) {
                allSuccess = false;
            }
        }

        if (allSuccess) {
            std::cout << "[+] All templates processed successfully" << std::endl;
        } else {
            std::cout << "[!] Warning: Some templates failed to process" << std::endl;
        }

        return allSuccess;
    }
};

void printUsage(const char* programName) {
    std::cout << "Usage: " << programName << " <image_path>" << std::endl;
    std::cout << "       " << programName << " --help" << std::endl;
    std::cout << "\nGenerate color schemes from images using ImageMagick" << std::endl;
    std::cout << "\nConfiguration file: ~/.config/cppwal/config.ini" << std::endl;
}

int main(int argc, char* argv[]) {
    try {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }
    
    std::string arg = argv[1];
    if (arg == "--help" || arg == "-h") {
        printUsage(argv[0]);
        return 0;
    }
    
    CppWal cppwal;
    
    if (!cppwal.initialize()) {
        std::cerr << "[-] Failed to initialize cppwal" << std::endl;
        return 1;
    }
    
    if (!cppwal.processImage(arg)) {
        std::cerr << "[-] Failed to process image: " << arg << std::endl;
        return 1;
    }
    
    return 0;
    } catch (const std::exception& ex) {
        std::cerr << "[!] Unhandled exception: " << ex.what() << std::endl;
        return 2;
    } catch (...) {
        std::cerr << "[!] Unknown fatal error occurred." << std::endl;
        return 2;
    }
}
