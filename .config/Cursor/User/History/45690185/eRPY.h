// Minimal INIReader.h from inih
#ifndef __INIREADER_H__
#define __INIREADER_H__
#include <string>
#include <map>
class INIReader {
public:
    INIReader(const std::string& filename);
    int ParseError() const;
    std::string Get(const std::string& section, const std::string& name, const std::string& default_value) const;
private:
    int _error;
    std::map<std::string, std::string> _values;
};
#endif 