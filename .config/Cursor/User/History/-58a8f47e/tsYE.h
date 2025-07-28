/* ini.h - simple INI file parser */
#ifndef __INI_H__
#define __INI_H__
#ifdef __cplusplus
extern "C" {
#endif

typedef int (*ini_handler)(void*, const char*, const char*, const char*);
int ini_parse(const char* filename, ini_handler handler, void* user);

#ifdef __cplusplus
}
#endif
#endif 