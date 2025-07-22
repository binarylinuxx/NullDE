#include "INIReader.h"
#include "ini.h"
#include <fstream>
#include <sstream>

static std::string make_key(const std::string& section, const std::string& name) {
    return section + "." + name;
}

static int ValueHandler(void* user, const char* section, const char* name, const char* value) {
    auto* reader = reinterpret_cast<INIReader*>(user);
    reader->_values[make_key(section, name)] = value ? value : "";
    return 1;
}

INIReader::INIReader(const std::string& filename) {
    _error = ini_parse(filename.c_str(), ValueHandler, this);
}

int INIReader::ParseError() const { return _error; }

std::string INIReader::Get(const std::string& section, const std::string& name, const std::string& default_value) const {
    auto it = _values.find(make_key(section, name));
    return it == _values.end() ? default_value : it->second;
} 