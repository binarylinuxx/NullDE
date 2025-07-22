#include "ini.h"
#include <stdio.h>
#include <string.h>
#define MAX_LINE 200

int ini_parse(const char* filename, ini_handler handler, void* user) {
    FILE* file = fopen(filename, "r");
    if (!file) return -1;
    char line[MAX_LINE];
    char section[50] = "";
    while (fgets(line, sizeof(line), file)) {
        char* start = line;
        while (*start == ' ' || *start == '\t') ++start;
        if (*start == ';' || *start == '#' || *start == '\n') continue;
        if (*start == '[') {
            char* end = strchr(start, ']');
            if (end) {
                *end = 0;
                strncpy(section, start + 1, sizeof(section) - 1);
                section[sizeof(section) - 1] = 0;
            }
        } else {
            char* eq = strchr(start, '=');
            if (eq) {
                *eq = 0;
                char* name = start;
                char* value = eq + 1;
                char* nl = strchr(value, '\n');
                if (nl) *nl = 0;
                while (*name == ' ' || *name == '\t') ++name;
                char* name_end = name + strlen(name) - 1;
                while (name_end > name && (*name_end == ' ' || *name_end == '\t')) *name_end-- = 0;
                while (*value == ' ' || *value == '\t') ++value;
                char* value_end = value + strlen(value) - 1;
                while (value_end > value && (*value_end == ' ' || *value_end == '\t')) *value_end-- = 0;
                handler(user, section, name, value);
            }
        }
    }
    fclose(file);
    return 0;
} 