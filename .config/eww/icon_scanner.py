#!/usr/bin/env python3

import os
import glob
import json
import subprocess
from pathlib import Path

class IconScanner:
    def __init__(self):
        self.icon_cache = {}
        self.desktop_entries = {}
        self.icon_themes = [
            "Tela-circle-dark",
            "hicolor", 
            "Adwaita",
            "gnome",
            "Papirus",
            "breeze"
        ]
        
    def scan_all_icons(self):
        """Сканирует все доступные иконки в системе"""
        print("=== Starting icon scan ===")
        
        # 1. Сканируем desktop файлы
        self.scan_desktop_entries()
        
        # 2. Сканируем директории с иконками
        self.scan_icon_directories()
        
        # 3. Создаем финальный кэш
        self.create_icon_cache()
        
        # 4. Сохраняем кэш
        self.save_cache()
        
        print(f"=== Scan complete: {len(self.icon_cache)} icons found ===")
        
    def scan_desktop_entries(self):
        """Сканирует все desktop файлы"""
        print("Scanning desktop entries...")
        
        desktop_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications", 
            f"{os.path.expanduser('~')}/.local/share/applications",
            "/var/lib/flatpak/exports/share/applications",
            f"{os.path.expanduser('~')}/.local/share/flatpak/exports/share/applications",
        ]
        
        # Добавляем Flatpak app directories
        flatpak_patterns = [
            "/var/lib/flatpak/app/*/current/active/files/share/applications",
            f"{os.path.expanduser('~')}/.local/share/flatpak/app/*/current/active/files/share/applications"
        ]
        
        for pattern in flatpak_patterns:
            desktop_dirs.extend(glob.glob(pattern))
        
        for desktop_dir in desktop_dirs:
            if not os.path.exists(desktop_dir):
                continue
                
            print(f"  Scanning: {desktop_dir}")
            
            for file in os.listdir(desktop_dir):
                if not file.endswith('.desktop'):
                    continue
                    
                filepath = os.path.join(desktop_dir, file)
                self.parse_desktop_file(filepath, file)
                
    def parse_desktop_file(self, filepath, filename):
        """Парсит desktop файл"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            name = None
            icon = None
            wm_class = None
            flatpak_id = None
            exec_line = None
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('Name=') and not line.startswith('Name['):
                    name = line.split('=', 1)[1]
                elif line.startswith('Icon='):
                    icon = line.split('=', 1)[1]
                elif line.startswith('StartupWMClass='):
                    wm_class = line.split('=', 1)[1]
                elif line.startswith('X-Flatpak='):
                    flatpak_id = line.split('=', 1)[1]
                elif line.startswith('Exec='):
                    exec_line = line.split('=', 1)[1]
            
            if name and icon:
                # Базовый ключ
                base_key = filename[:-8]  # убираем .desktop
                
                entry = {
                    'name': name,
                    'icon': icon,
                    'wm_class': wm_class,
                    'flatpak_id': flatpak_id, 
                    'exec': exec_line,
                    'desktop_file': filepath
                }
                
                # Добавляем различные варианты ключей
                keys_to_add = [base_key.lower()]
                
                if wm_class:
                    keys_to_add.append(wm_class.lower())
                
                if flatpak_id:
                    keys_to_add.append(flatpak_id.lower())
                    # Добавляем части Flatpak ID
                    parts = flatpak_id.split('.')
                    if len(parts) > 1:
                        keys_to_add.append(parts[-1].lower())  # последняя часть
                        if len(parts) > 2:
                            keys_to_add.append('.'.join(parts[-2:]).lower())  # последние 2 части
                
                # Добавляем все варианты в кэш
                for key in keys_to_add:
                    if key not in self.desktop_entries:
                        self.desktop_entries[key] = entry
                        
        except Exception as e:
            # Игнорируем ошибки парсинга
            pass
    
    def scan_icon_directories(self):
        """Сканирует директории с иконками"""
        print("Scanning icon directories...")
        
        icon_base_dirs = [
            "/usr/share/icons",
            "/usr/local/share/icons",
            f"{os.path.expanduser('~')}/.local/share/icons",
            f"{os.path.expanduser('~')}/.icons",
            "/var/lib/flatpak/exports/share/icons",
            f"{os.path.expanduser('~')}/.local/share/flatpak/exports/share/icons"
        ]
        
        for base_dir in icon_base_dirs:
            if not os.path.exists(base_dir):
                continue
                
            print(f"  Scanning: {base_dir}")
            
            for theme in self.icon_themes:
                theme_dir = os.path.join(base_dir, theme)
                if os.path.exists(theme_dir):
                    self.scan_theme_directory(theme_dir, theme)
    
    def scan_theme_directory(self, theme_dir, theme_name):
        """Сканирует конкретную тему иконок"""
        app_dirs = []
        
        # Ищем папки apps в разных размерах и scalable
        for root, dirs, files in os.walk(theme_dir):
            if 'apps' in dirs:
                app_dirs.append(os.path.join(root, 'apps'))
        
        for app_dir in app_dirs:
            try:
                for filename in os.listdir(app_dir):
                    if filename.endswith(('.svg', '.png', '.xpm')):
                        icon_name = filename.rsplit('.', 1)[0]  # убираем расширение
                        icon_path = os.path.join(app_dir, filename)
                        
                        # Определяем приоритет (Tela > hicolor > остальные)
                        priority = 0
                        if theme_name == "Tela-circle-dark":
                            priority = 100
                        elif theme_name == "hicolor":
                            priority = 50
                        elif 'scalable' in app_dir:
                            priority += 10
                        elif '48' in app_dir or '64' in app_dir:
                            priority += 5
                            
                        # SVG имеет приоритет над PNG
                        if filename.endswith('.svg'):
                            priority += 2
                        
                        key = icon_name.lower()
                        
                        # Добавляем только если приоритет выше или иконки еще нет
                        if key not in self.icon_cache or self.icon_cache[key]['priority'] < priority:
                            self.icon_cache[key] = {
                                'path': icon_path,
                                'theme': theme_name,
                                'priority': priority,
                                'size_dir': os.path.basename(os.path.dirname(app_dir))
                            }
                            
            except Exception as e:
                continue
    
    def create_icon_cache(self):
        """Создает финальный кэш иконок"""
        print("Creating final icon cache...")
        
        # Объединяем данные из desktop файлов и сканирования иконок
        final_cache = {}
        
        # Сначала добавляем все иконки из desktop файлов
        for key, entry in self.desktop_entries.items():
            icon_name = entry['icon']
            
            # Если иконка указана как путь, используем его
            if icon_name.startswith('/') and os.path.exists(icon_name):
                final_cache[key] = {
                    'name': entry['name'],
                    'icon_path': icon_name,
                    'source': 'desktop_file_absolute',
                    'wm_class': entry.get('wm_class'),
                    'flatpak_id': entry.get('flatpak_id')
                }
            else:
                # Ищем иконку в кэше иконок
                icon_key = icon_name.lower()
                if icon_key in self.icon_cache:
                    final_cache[key] = {
                        'name': entry['name'],
                        'icon_path': self.icon_cache[icon_key]['path'],
                        'source': f"icon_theme_{self.icon_cache[icon_key]['theme']}",
                        'wm_class': entry.get('wm_class'),
                        'flatpak_id': entry.get('flatpak_id')
                    }
                else:
                    # Иконка не найдена, но запишем entry
                    final_cache[key] = {
                        'name': entry['name'],
                        'icon_path': None,
                        'icon_name': icon_name,
                        'source': 'desktop_file_missing_icon',
                        'wm_class': entry.get('wm_class'),
                        'flatpak_id': entry.get('flatpak_id')
                    }
        
        # Добавляем иконки, для которых нет desktop файлов
        for icon_key, icon_data in self.icon_cache.items():
            if icon_key not in final_cache:
                # Создаем красивое имя из названия иконки
                display_name = icon_key.replace('-', ' ').replace('_', ' ').title()
                final_cache[icon_key] = {
                    'name': display_name,
                    'icon_path': icon_data['path'],
                    'source': f"icon_only_{icon_data['theme']}",
                    'wm_class': None,
                    'flatpak_id': None
                }
        
        self.icon_cache = final_cache
    
    def save_cache(self):
        """Сохраняет кэш в файл"""
        cache_dir = f"{os.path.expanduser('~')}/.cache/eww_dock"
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, "icon_cache.json")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.icon_cache, f, ensure_ascii=False, indent=2)
        
        print(f"Cache saved to: {cache_file}")
    
    def search_icons(self, query):
        """Поиск иконок по запросу"""
        query = query.lower()
        results = []
        
        for key, data in self.icon_cache.items():
            if (query in key or 
                query in data['name'].lower() or
                (data.get('wm_class') and query in data['wm_class'].lower()) or
                (data.get('flatpak_id') and query in data['flatpak_id'].lower())):
                
                results.append({
                    'key': key,
                    'name': data['name'],
                    'icon_path': data.get('icon_path'),
                    'source': data['source'],
                    'wm_class': data.get('wm_class'),
                    'flatpak_id': data.get('flatpak_id')
                })
        
        return results
    
    def print_stats(self):
        """Выводит статистику"""
        total = len(self.icon_cache)
        with_icons = len([x for x in self.icon_cache.values() if x.get('icon_path')])
        without_icons = total - with_icons
        
        sources = {}
        for data in self.icon_cache.values():
            source = data['source']
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n=== STATISTICS ===")
        print(f"Total entries: {total}")
        print(f"With icons: {with_icons}")
        print(f"Without icons: {without_icons}")
        print(f"\nSources:")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count}")

def main():
    import sys
    
    scanner = IconScanner()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 icon_scanner.py scan          - Scan all icons")
        print("  python3 icon_scanner.py search <term> - Search for icons")
        print("  python3 icon_scanner.py stats         - Show statistics")
        print("  python3 icon_scanner.py list          - List all found entries")
        return
    
    command = sys.argv[1]
    
    if command == "scan":
        scanner.scan_all_icons()
        scanner.print_stats()
        
    elif command == "search" and len(sys.argv) > 2:
        # Загружаем кэш
        cache_file = f"{os.path.expanduser('~')}/.cache/eww_dock/icon_cache.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                scanner.icon_cache = json.load(f)
        
        query = sys.argv[2]
        results = scanner.search_icons(query)
        
        print(f"=== Search results for '{query}' ===")
        for result in results[:20]:  # Показываем только первые 20
            icon_status = "✓" if result['icon_path'] and os.path.exists(result['icon_path']) else "✗"
            print(f"{icon_status} found: {result['key']}")
            print(f"   name: {result['name']}")
            if result['icon_path']:
                print(f"   found-icon-for-the-app: {result['icon_path']}")
            if result['wm_class']:
                print(f"   wm_class: {result['wm_class']}")
            if result['flatpak_id']:
                print(f"   flatpak_id: {result['flatpak_id']}")
            print(f"   source: {result['source']}")
            print()
            
    elif command == "stats":
        # Загружаем кэш
        cache_file = f"{os.path.expanduser('~')}/.cache/eww_dock/icon_cache.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                scanner.icon_cache = json.load(f)
            scanner.print_stats()
        else:
            print("No cache found. Run 'scan' first.")
            
    elif command == "list":
        # Загружаем кэш
        cache_file = f"{os.path.expanduser('~')}/.cache/eww_dock/icon_cache.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                scanner.icon_cache = json.load(f)
            
            print("=== All found entries ===")
            for key, data in sorted(scanner.icon_cache.items()):
                icon_status = "✓" if data.get('icon_path') and os.path.exists(data.get('icon_path', '')) else "✗"
                print(f"{icon_status} found: {key}")
                print(f"   name: {data['name']}")
                if data.get('icon_path'):
                    print(f"   found-icon-for-the-app: {data['icon_path']}")
                print()
        else:
            print("No cache found. Run 'scan' first.")

if __name__ == '__main__':
    main()
