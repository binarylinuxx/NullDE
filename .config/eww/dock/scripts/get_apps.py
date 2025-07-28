#!/usr/bin/env python3

import glob
import json
import subprocess
import socket
import os
import threading
import time
from pathlib import Path
from collections import defaultdict
import configparser

class HyprlandAppMonitor:
    def __init__(self):
        self.apps = {}
        self.socket_path = self.get_hyprland_socket()
        self.desktop_entries = self.load_desktop_entries()
        self.config_dir = f"{os.path.expanduser('~')}/.config/eww/dock"
        self.usage_stats = self.load_usage_stats()
        self.pinned_apps = self.load_pinned_apps()
        
        # Создаем конфиг директорию если не существует
        os.makedirs(self.config_dir, exist_ok=True)
        
    def get_hyprland_socket(self):
        """Get Hyprland IPC socket path"""
        hypr_instance = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
        if not hypr_instance:
            raise Exception("Not running under Hyprland")
        return f"/tmp/hypr/{hypr_instance}/.socket2.sock"
    
    def load_usage_stats(self):
        """Загрузить статистику использования приложений"""
        stats_file = os.path.join(self.config_dir, "app_usage.json")
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_usage_stats(self):
        """Сохранить статистику использования"""
        stats_file = os.path.join(self.config_dir, "app_usage.json")
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.usage_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving usage stats: {e}")
    
    def load_pinned_apps(self):
        """Загрузить закрепленные приложения"""
        pinned_file = os.path.join(self.config_dir, "pinned_apps.json")
        try:
            if os.path.exists(pinned_file):
                with open(pinned_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Дефолтные закрепленные приложения
        default_pinned = [
            "firefox",
            "org.gnome.Nautilus",
            "code",
            "discord",
            "telegram-desktop",
            "spotify"
        ]
        self.save_pinned_apps(default_pinned)
        return default_pinned
    
    def save_pinned_apps(self, pinned_apps=None):
        """Сохранить закрепленные приложения"""
        if pinned_apps is None:
            pinned_apps = self.pinned_apps
            
        pinned_file = os.path.join(self.config_dir, "pinned_apps.json")
        try:
            with open(pinned_file, 'w') as f:
                json.dump(pinned_apps, f, indent=2)
        except Exception as e:
            print(f"Error saving pinned apps: {e}")
    
    def update_usage_stats(self, app_class):
        """Обновить статистику использования приложения"""
        if not app_class:
            return
            
        current_time = time.time()
        
        if app_class not in self.usage_stats:
            self.usage_stats[app_class] = {
                'count': 0,
                'last_used': current_time,
                'total_time': 0
            }
        
        self.usage_stats[app_class]['count'] += 1
        self.usage_stats[app_class]['last_used'] = current_time
        
        # Сохраняем каждые 10 запусков
        if self.usage_stats[app_class]['count'] % 10 == 0:
            self.save_usage_stats()
    
    def get_frequent_apps(self, limit=10):
        """Получить часто используемые приложения"""
        # Сортируем по количеству использований и времени последнего использования
        sorted_apps = sorted(
            self.usage_stats.items(),
            key=lambda x: (x[1]['count'], x[1]['last_used']),
            reverse=True
        )
        
        return [app[0] for app in sorted_apps[:limit]]
    
    def load_desktop_entries(self):
        """Load desktop entries to map class names to icons"""
        desktop_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            f"{os.path.expanduser('~')}/.local/share/applications",
            "/var/lib/flatpak/exports/share/applications",
            f"{os.path.expanduser('~')}/.local/share/flatpak/exports/share/applications",
            # Additional Flatpak paths
            "/var/lib/flatpak/app/*/*/active/files/share/applications",
            f"{os.path.expanduser('~')}/.local/share/flatpak/app/*/*/active/files/share/applications"
        ]
        
        # Expand glob patterns
        expanded_dirs = []
        for pattern in desktop_dirs:
            expanded_dirs.extend(glob.glob(pattern))
        
        entries = {}
        
        for desktop_dir in expanded_dirs:
            if not os.path.exists(desktop_dir):
                continue
                
            for file in os.listdir(desktop_dir):
                if not file.endswith('.desktop'):
                    continue
                    
                filepath = os.path.join(desktop_dir, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    name = None
                    icon = None
                    wm_class = None
                    flatpak_id = None
                    executable = None
                    no_display = False
                    
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
                            executable = line.split('=', 1)[1]
                        elif line.startswith('NoDisplay=true'):
                            no_display = True
                    
                    # Пропускаем скрытые приложения
                    if no_display:
                        continue
                    
                    if name and icon:
                        # Use WMClass if available, otherwise use filename without .desktop
                        key = wm_class if wm_class else file[:-8]
                        entries[key.lower()] = {
                            'name': name,
                            'icon': icon,
                            'class': key,
                            'executable': executable,
                            'desktop_file': filepath,
                        }
                        
                        # Add Flatpak ID if available
                        if flatpak_id:
                            entries[flatpak_id.lower()] = entries[key.lower()]
                        
                        # Also add common name variations
                        if '.' in key:
                            parts = key.split('.')
                            if len(parts) > 1:
                                entries[parts[-1].lower()] = entries[key.lower()]
                    
                except Exception as e:
                    continue
                    
        return entries
    
    def get_icon_path(self, icon_name, class_name=""):
        """Get icon path - теперь всегда возвращает что-то"""
        # Список возможных иконок по умолчанию в порядке приоритета
        fallback_icons = [
            # Tela Circle Dark theme
            "/usr/share/icons/Tela-circle-dark/scalable/apps/application-x-executable.svg",
            "/usr/share/icons/Tela-circle-dark/48x48/apps/application-x-executable.svg",
            "/usr/share/icons/Tela-circle-dark/scalable/apps/applications-other.svg",
            "/usr/share/icons/Tela-circle-dark/48x48/apps/applications-other.svg",
            # User local Tela
            f"{os.path.expanduser('~')}/.local/share/icons/Tela-circle-dark/scalable/apps/application-x-executable.svg",
            f"{os.path.expanduser('~')}/.local/share/icons/Tela-circle-dark/48x48/apps/application-x-executable.svg",
            # System fallbacks
            "/usr/share/icons/hicolor/scalable/apps/application-x-executable.svg",
            "/usr/share/icons/hicolor/48x48/apps/application-x-executable.png",
            "/usr/share/pixmaps/application-x-executable.png",
            # Adwaita theme
            "/usr/share/icons/Adwaita/scalable/apps/application-x-executable-symbolic.svg",
            "/usr/share/icons/Adwaita/48x48/apps/application-x-executable.png",
            # Generic fallbacks
            "/usr/share/icons/gnome/48x48/apps/gnome-applications.png",
            "/usr/share/pixmaps/gnome-applications.png",
        ]
        
        if not icon_name:
            # Если иконки нет, сразу идем к фоллбэкам
            for fallback in fallback_icons:
                if os.path.exists(fallback):
                    return fallback
            # Если ничего не найдено, создаем простую текстовую иконку
            return self.create_text_icon(class_name)
    
        # 1. Check if this is a Flatpak app icon (already full path)
        if isinstance(icon_name, str) and icon_name.startswith('/'):
            if os.path.exists(icon_name):
                return icon_name
            # If not, extract the basename and continue with normal lookup
            icon_name = os.path.basename(icon_name).split('.')[0]
    
        # 2. Standard icon lookup
        icon_dirs = [
            # Tela Circle Dark theme (preferred)
            "/usr/share/icons/Tela-circle-dark/scalable/apps",
            "/usr/share/icons/Tela-circle-dark/48x48/apps",
            "/usr/share/icons/Tela-circle-dark/64x64/apps",
            "/usr/share/icons/Tela-circle-dark/96x96/apps",
            "/usr/share/icons/Tela-circle-dark/128x128/apps",
            f"{os.path.expanduser('~')}/.local/share/icons/Tela-circle-dark/scalable/apps",
            f"{os.path.expanduser('~')}/.local/share/icons/Tela-circle-dark/48x48/apps",
            # System icon themes
            "/usr/share/icons/hicolor/scalable/apps",
            "/usr/share/icons/hicolor/48x48/apps",
            "/usr/share/icons/hicolor/64x64/apps",
            "/usr/share/icons/Adwaita/scalable/apps",
            "/usr/share/icons/Adwaita/48x48/apps",
            # Flatpak icon locations
            "/var/lib/flatpak/exports/share/icons/hicolor/scalable/apps",
            "/var/lib/flatpak/exports/share/icons/hicolor/48x48/apps",
            f"{os.path.expanduser('~')}/.local/share/flatpak/exports/share/icons/hicolor/scalable/apps",
        ]
    
        extensions = ['.svg', '.png']
    
        # Try to find the icon
        for icon_dir in icon_dirs:
            if os.path.exists(icon_dir):
                for ext in extensions:
                    icon_path = os.path.join(icon_dir, f"{icon_name}{ext}")
                    if os.path.exists(icon_path):
                        return icon_path
    
        # 3. Try some common name variations
        variations = [
            icon_name.lower(),
            icon_name.replace('-', '_'),
            icon_name.replace('_', '-'),
        ]
        
        if '.' in icon_name:  # Flatpak app ID
            parts = icon_name.split('.')
            variations.extend([
                parts[-1],  # last part
                '.'.join(parts[-2:]),  # last two parts
            ])
        
        for variation in variations:
            for icon_dir in icon_dirs:
                if os.path.exists(icon_dir):
                    for ext in extensions:
                        icon_path = os.path.join(icon_dir, f"{variation}{ext}")
                        if os.path.exists(icon_path):
                            return icon_path
    
        # 4. Fallback to default icons
        for fallback in fallback_icons:
            if os.path.exists(fallback):
                return fallback
                
        # 5. Last resort - create a text-based icon placeholder
        return self.create_text_icon(class_name or icon_name)
    
    def create_text_icon(self, app_name):
        """Create a simple text-based SVG icon as fallback"""
        if not app_name:
            app_name = "App"
            
        # Get first 2 characters for the icon
        text = app_name[:2].upper()
        
        # Create cache directory
        cache_dir = f"{os.path.expanduser('~')}/.cache/eww_dock_icons"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create SVG file
        svg_path = os.path.join(cache_dir, f"{app_name.lower().replace(' ', '_')}.svg")
        
        if not os.path.exists(svg_path):
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="20" fill="#444444" stroke="#666666" stroke-width="2"/>
  <text x="24" y="32" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle" fill="#ffffff">{text}</text>
</svg>'''
            
            try:
                with open(svg_path, 'w') as f:
                    f.write(svg_content)
            except:
                pass
        
        return svg_path
    
    def normalize_class_name(self, class_name):
        """Нормализовать class name для лучшего сопоставления"""
        if not class_name:
            return class_name
            
        # Общие сопоставления для популярных приложений
        class_mappings = {
            'telegram-desktop': 'telegram-desktop',
            'telegramdesktop': 'telegram-desktop',
            'org.telegram.desktop': 'telegram-desktop',
            'discord': 'discord',
            'Discord': 'discord',
            'firefox': 'firefox',
            'Firefox': 'firefox',
            'Mozilla Firefox': 'firefox',
            'google-chrome': 'google-chrome',
            'Google-chrome': 'google-chrome',
            'chromium': 'chromium',
            'Chromium': 'chromium',
            'code': 'code',
            'Code': 'code',
            'visual-studio-code': 'code',
            'code-oss': 'code',
            'spotify': 'spotify',
            'Spotify': 'spotify',
            'nautilus': 'org.gnome.Nautilus',
            'Nautilus': 'org.gnome.Nautilus',
            'org.gnome.Nautilus': 'org.gnome.Nautilus',
            'thunar': 'thunar',
            'Thunar': 'thunar',
        }
        
        # Проверяем прямые сопоставления
        if class_name in class_mappings:
            return class_mappings[class_name]
            
        # Проверяем case-insensitive сопоставления
        class_lower = class_name.lower()
        for key, value in class_mappings.items():
            if key.lower() == class_lower:
                return value
                
        return class_name
    def get_app_info(self, class_name, title=""):
        """Get app info - теперь всегда возвращает данные"""
        if not class_name:
            class_name = "Unknown"
            
        # Нормализуем class name
        normalized_class = self.normalize_class_name(class_name)
        class_lower = normalized_class.lower()
        
        # First try exact match in desktop entries
        if class_lower in self.desktop_entries:
            entry = self.desktop_entries[class_lower]
            return {
                'name': entry['name'],
                'icon': self.get_icon_path(entry['icon'], class_name),
                'class': normalized_class,  # Используем нормализованный class
                'executable': entry.get('executable', ''),
                'desktop_file': entry.get('desktop_file', '')
            }
        
        # Try variations for Flatpak apps
        if '.' in normalized_class and len(normalized_class.split('.')) > 2:
            parts = normalized_class.split('.')
            variations = [
                class_lower,
                '.'.join(parts[-2:]),
                parts[-1],
                f"{parts[-1]}-desktop",
                f"{parts[-1]}.desktop"
            ]
            
            for variation in variations:
                if variation in self.desktop_entries:
                    entry = self.desktop_entries[variation]
                    return {
                        'name': entry['name'],
                        'icon': self.get_icon_path(entry['icon'], class_name),
                        'class': normalized_class,
                        'executable': entry.get('executable', ''),
                        'desktop_file': entry.get('desktop_file', '')
                    }
        
        # Try to extract a readable name from class name
        display_name = normalized_class
        if '.' in normalized_class:
            # For reverse DNS notation (e.g. org.example.App -> App)
            display_name = normalized_class.split('.')[-1]
        
        # Capitalize and make readable
        display_name = display_name.replace('-', ' ').replace('_', ' ').title()
        
        # If we have a window title and it's shorter/more readable, use it
        if title and len(title) < 30 and not any(x in title.lower() for x in ['untitled', 'unnamed', 'новый', 'new']):
            # Remove common window title suffixes
            clean_title = title
            for suffix in [' - Mozilla Firefox', ' - Google Chrome', ' - Chromium', ' - Visual Studio Code']:
                if clean_title.endswith(suffix):
                    clean_title = clean_title[:-len(suffix)]
                    break
            if len(clean_title) > 0 and len(clean_title) < len(display_name):
                display_name = clean_title
        
        # Always return something - даже для неизвестных приложений
        return {
            'name': display_name,
            'icon': self.get_icon_path(class_lower, class_name),
            'class': normalized_class,
            'executable': '',
            'desktop_file': ''
        }
    
    def get_current_windows(self):
        """Get ALL currently open windows from Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'clients', '-j'], 
                                  capture_output=True, text=True)
            windows = json.loads(result.stdout)
            
            apps = {}
            for window in windows:
                class_name = window.get('class', '')
                title = window.get('title', '')
                
                # Пропускаем только полностью пустые окна или специальные
                if not class_name and not title:
                    continue
                    
                # Пропускаем специальные системные окна
                if class_name in ['', 'null'] and any(x in title.lower() for x in ['desktop', 'wallpaper', 'background']):
                    continue
                
                # Нормализуем class name
                normalized_class = self.normalize_class_name(class_name) if class_name else f"window_{title[:20]}"
                
                if normalized_class not in apps:
                    app_info = self.get_app_info(class_name, title)
                    apps[normalized_class] = {
                        'name': app_info['name'],
                        'icon': app_info['icon'],
                        'class': normalized_class,
                        'executable': app_info.get('executable', ''),
                        'desktop_file': app_info.get('desktop_file', ''),
                        'windows': [],
                        'is_running': True
                    }
                
                apps[normalized_class]['windows'].append({
                    'address': window.get('address', ''),
                    'title': title,
                    'workspace': window.get('workspace', {}).get('name', '1')
                })
            
            return apps
            
        except Exception as e:
            print(f"Error getting windows: {e}")
            return {}
    
    def get_all_apps(self):
        """Получить все приложения (открытые + закрепленные + часто используемые)"""
        # Получаем открытые окна
        running_apps = self.get_current_windows()
        
        # Создаем итоговый список
        all_apps = {}
        
        # Сначала добавляем закрепленные приложения
        for pinned_class in self.pinned_apps:
            app_info = self.get_app_info(pinned_class)
            all_apps[pinned_class] = {
                'name': app_info['name'],
                'icon': app_info['icon'],
                'class': pinned_class,
                'executable': app_info.get('executable', ''),
                'desktop_file': app_info.get('desktop_file', ''),
                'windows': [],
                'is_running': False,
                'is_pinned': True
            }
        
        # Затем обновляем данные для запущенных приложений
        for class_name, app_data in running_apps.items():
            if class_name in all_apps:
                # Приложение уже есть в списке (закреплено) - обновляем данные
                all_apps[class_name]['windows'] = app_data['windows']
                all_apps[class_name]['is_running'] = True
            else:
                # Новое незакрепленное приложение
                all_apps[class_name] = app_data
                all_apps[class_name]['is_pinned'] = False
        
        # Добавляем часто используемые приложения (которые не открыты и не закреплены)
        frequent_apps = self.get_frequent_apps(3)  # Топ 3 часто используемых
        for freq_class in frequent_apps:
            if freq_class not in all_apps:
                app_info = self.get_app_info(freq_class)
                all_apps[freq_class] = {
                    'name': app_info['name'],
                    'icon': app_info['icon'],
                    'class': freq_class,
                    'executable': app_info.get('executable', ''),
                    'desktop_file': app_info.get('desktop_file', ''),
                    'windows': [],
                    'is_running': False,
                    'is_pinned': False,
                    'is_frequent': True
                }
        
        return all_apps
    
    def launch_app(self, class_name):
        """Запустить приложение"""
        try:
            # Обновляем статистику использования
            self.update_usage_stats(class_name)
            
            # Пробуем найти в desktop entries
            class_lower = class_name.lower()
            if class_lower in self.desktop_entries:
                desktop_file = self.desktop_entries[class_lower].get('desktop_file')
                if desktop_file and os.path.exists(desktop_file):
                    subprocess.Popen(['gtk-launch', os.path.basename(desktop_file)[:-8]])
                    return
                
                executable = self.desktop_entries[class_lower].get('executable')
                if executable:
                    # Очищаем executable от аргументов
                    exec_clean = executable.split()[0]
                    subprocess.Popen([exec_clean])
                    return
            
            # Если не нашли в desktop entries, пробуем запустить напрямую
            subprocess.Popen([class_name])
            
        except Exception as e:
            print(f"Error launching app {class_name}: {e}")
    
    def listen_to_events(self):
        """Listen to Hyprland events"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            
            while True:
                data = sock.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                # Update apps when window events occur
                if any(event in data for event in ['openwindow', 'closewindow', 'windowtitle']):
                    # Извлекаем class name из события для обновления статистики
                    if 'openwindow' in data:
                        try:
                            parts = data.split(',')
                            if len(parts) >= 2:
                                class_name = parts[1]
                                self.update_usage_stats(class_name)
                        except:
                            pass
                    
                    self.update_apps()
                    
        except Exception as e:
            print(f"Error listening to events: {e}")
            # Fallback to polling
            while True:
                self.update_apps()
                time.sleep(2)
    
    def update_apps(self):
        """Update apps and output JSON"""
        self.apps = self.get_all_apps()
        self.output_json()
    
    def output_json(self):
        """Output current apps as JSON for eww"""
        apps_list = []
        
        # Создаем словарь порядка для закрепленных приложений
        pinned_order = {app: i for i, app in enumerate(self.pinned_apps)}
        
        # Разделяем приложения на категории
        pinned_apps = []
        running_unpinned = []
        frequent_apps = []
        
        for class_name, app_data in self.apps.items():
            app_info = {
                'name': app_data['name'],
                'icon': app_data['icon'],
                'class': app_data['class'],
                'window_count': len(app_data['windows']),
                'address': app_data['windows'][0]['address'] if app_data['windows'] else '',
                'is_running': app_data.get('is_running', False),
                'is_pinned': app_data.get('is_pinned', False),
                'is_frequent': app_data.get('is_frequent', False),
                'pinned_position': pinned_order.get(class_name, -1)
            }
            
            if app_info['is_pinned']:
                pinned_apps.append(app_info)
            elif app_info['is_running']:
                running_unpinned.append(app_info)
            elif app_info['is_frequent']:
                frequent_apps.append(app_info)
        
        # Сортируем каждую категорию
        pinned_apps.sort(key=lambda x: x['pinned_position'])  # По порядку закрепления
        running_unpinned.sort(key=lambda x: x['name'].lower())  # По алфавиту
        frequent_apps.sort(key=lambda x: x['name'].lower())  # По алфавиту
        
        # Объединяем в правильном порядке
        apps_list = pinned_apps + running_unpinned + frequent_apps
        
        # Удаляем служебное поле
        for app in apps_list:
            app.pop('pinned_position', None)
        
        output = {
            'apps': apps_list,
            'count': len(apps_list)
        }
        
        print(json.dumps(output, ensure_ascii=False))
    
    def focus_app(self, class_name):
        """Focus application by class name or launch if not running"""
        try:
            if class_name == 'unknown':
                return
            
            # Проверяем, запущено ли приложение
            running_apps = self.get_current_windows()
            
            if class_name in running_apps:
                # Приложение запущено - фокусируемся на него
                subprocess.run(['hyprctl', 'dispatch', 'focuswindow', f'class:{class_name}'])
            else:
                # Приложение не запущено - запускаем его
                self.launch_app(class_name)
                
        except Exception as e:
            print(f"Error focusing/launching app: {e}")
    
    def pin_app(self, class_name):
        """Закрепить приложение"""
        if class_name and class_name not in self.pinned_apps:
            self.pinned_apps.append(class_name)
            self.save_pinned_apps()
            print(f"Pinned {class_name}")
    
    def unpin_app(self, class_name):
        """Открепить приложение"""
        if class_name in self.pinned_apps:
            self.pinned_apps.remove(class_name)
            self.save_pinned_apps()
            print(f"Unpinned {class_name}")

def main():
    import sys
    
    monitor = HyprlandAppMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'focus' and len(sys.argv) > 2:
            monitor.focus_app(sys.argv[2])
            return
        elif sys.argv[1] == 'list':
            monitor.update_apps()
            return
        elif sys.argv[1] == 'pin' and len(sys.argv) > 2:
            monitor.pin_app(sys.argv[2])
            return
        elif sys.argv[1] == 'unpin' and len(sys.argv) > 2:
            monitor.unpin_app(sys.argv[2])
            return
        elif sys.argv[1] == 'launch' and len(sys.argv) > 2:
            monitor.launch_app(sys.argv[2])
            return
        elif sys.argv[1] == 'debug':
            print("=== All Apps ===")
            apps = monitor.get_all_apps()
            for class_name, app_data in apps.items():
                print(f"Class: {class_name}")
                print(f"  Name: {app_data['name']}")
                print(f"  Icon: {app_data['icon']}")
                print(f"  Icon exists: {os.path.exists(app_data['icon']) if app_data['icon'] else False}")
                print(f"  Windows: {len(app_data['windows'])}")
                print(f"  Running: {app_data.get('is_running', False)}")
                print(f"  Pinned: {app_data.get('is_pinned', False)}")
                print(f"  Frequent: {app_data.get('is_frequent', False)}")
                print()
            print(f"\nPinned apps: {monitor.pinned_apps}")
            print(f"Usage stats: {monitor.usage_stats}")
            return
        elif sys.argv[1] == 'stats':
            print("=== Usage Statistics ===")
            for app, stats in monitor.usage_stats.items():
                print(f"{app}: {stats['count']} times, last used: {time.ctime(stats['last_used'])}")
            return
    
    # Initial output
    monitor.update_apps()
    
    # Start event listener
    monitor.listen_to_events()

if __name__ == '__main__':
    main()
