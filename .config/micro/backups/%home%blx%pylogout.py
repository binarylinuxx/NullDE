#!/usr/bin/env python3

import gi
import subprocess
import argparse
import sys
import os
import configparser
from pathlib import Path

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkX11

class LogoutMenu(Gtk.Window):
    def __init__(self, config):
        super().__init__(title="Logout Menu")
        self.config = config
        self.use_runit = config.getboolean('DEFAULT', 'use_runit', fallback=False)
        
        # Fullscreen setup
        self.set_default_size(Gdk.Screen.width(), Gdk.Screen.height())
        self.fullscreen()
        
        # Window properties for compositors
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        
        # Make window click-through (for some WMs)
        self.set_accept_focus(True)
        
        # Main container
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(int(config.get('Layout', 'row_spacing', fallback=20)))
        self.grid.set_column_spacing(int(config.get('Layout', 'column_spacing', fallback=20)))
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.add(self.grid)
        
        # Create buttons based on config
        self.buttons = []
        for section in config.sections():
            if section.startswith('Button/'):
                btn_name = section.split('/')[1]
                if config.getboolean(section, 'enabled', fallback=True):
                    self.buttons.append((
                        config.get(section, 'label', fallback=btn_name),
                        config.get(section, 'icon', fallback='dialog-question-symbolic'),
                        getattr(self, f'on_{btn_name.lower()}_clicked'),
                        config.get(section, 'command', fallback=None)
                    ))
        
        # Arrange buttons in grid
        columns = int(config.get('Layout', 'columns', fallback=2))
        for i, (text, icon, callback, cmd) in enumerate(self.buttons):
            btn = self.create_button(text, icon, callback)
            col = i % columns
            row = i // columns
            self.grid.attach(btn, col, row, 1, 1)
        
        # Connect key press event
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", lambda w, e: self.close())
        self.connect("button-press-event", self.on_bg_click)
    
    def create_button(self, text, icon_name, callback):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        icon.set_pixel_size(64)
        
        # Label
        label = Gtk.Label(label=text)
        
        box.pack_start(icon, True, True, 0)
        box.pack_start(label, True, True, 0)
        button.add(box)
        button.connect("clicked", callback)
        button.get_style_context().add_class("logout-button")
        button.set_size_request(200, 200)
        return button
    
    def execute_command(self, command):
        if not command:
            return
            
        try:
            if command.startswith('!'):
                # Direct command execution
                subprocess.run(command[1:], shell=True)
            elif self.use_runit:
                if command in ["suspend", "hibernate"]:
                    subprocess.run(["loginctl", command])
                elif command == "lock":
                    self.lock_screen()
                elif command == "logout":
                    self.logout()
                else:
                    subprocess.run(["loginctl", command, "-i"])
            else:
                if command == "lock":
                    self.lock_screen()
                elif command == "logout":
                    self.logout()
                else:
                    subprocess.run(["systemctl", command])
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
    
    def lock_screen(self):
        lock_cmd = self.config.get('Commands', 'lock', fallback=None)
        if lock_cmd:
            subprocess.Popen(lock_cmd.split())
            return
            
        # Fallback to common lock commands
        for cmd in ["swaylock", "i3lock", "slock"]:
            try:
                subprocess.Popen([cmd])
                return
            except:
                continue
        print("No lock screen utility found", file=sys.stderr)
    
    def logout(self):
        logout_cmd = self.config.get('Commands', 'logout', fallback=None)
        if logout_cmd:
            subprocess.run(logout_cmd.split())
            return
            
        if "WAYLAND_DISPLAY" in os.environ:
            try:
                subprocess.run(["hyprctl", "dispatch", "exit"])
                return
            except:
                try:
                    subprocess.run(["swaymsg", "exit"])
                    return
                except:
                    pass
        
        wm = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "i3" in wm:
            subprocess.run(["i3-msg", "exit"])
        elif "qtile" in wm:
            subprocess.run(["qtile", "cmd-obj", "-o", "cmd", "-f", "shutdown"])
        else:
            subprocess.run(["loginctl", "terminate-user", os.getenv("USER")])
    
    # Button handlers
    def on_lock_clicked(self, button):
        self.execute_command(self.get_button_command("lock"))
        self.close()
    
    def on_logout_clicked(self, button):
        self.execute_command(self.get_button_command("logout"))
        self.close()
    
    def on_reboot_clicked(self, button):
        self.execute_command(self.get_button_command("reboot"))
        self.close()
    
    def on_shutdown_clicked(self, button):
        self.execute_command(self.get_button_command("shutdown"))
        self.close()
    
    def on_suspend_clicked(self, button):
        self.execute_command(self.get_button_command("suspend"))
        self.close()
    
    def on_hibernate_clicked(self, button):
        self.execute_command(self.get_button_command("hibernate"))
        self.close()
    
    def on_cancel_clicked(self, button):
        self.close()
    
    def get_button_command(self, btn_name):
        for text, icon, callback, cmd in self.buttons:
            if btn_name.lower() in text.lower():
                return cmd
        return None
    
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
    
    def on_bg_click(self, widget, event):
        if event.button == 1:
            self.close()

def load_config():
    config = configparser.ConfigParser()
    
    # Default configuration
    config.read_dict({
        'DEFAULT': {
            'use_runit': 'False'
        },
        'Layout': {
            'columns': '2',
            'row_spacing': '20',
            'column_spacing': '20',
            'background_color': 'rgba(0, 0, 0, 0.7)',
            'button_color': 'rgba(40, 40, 40, 0.8)',
            'button_hover_color': 'rgba(60, 60, 60, 0.9)',
            'button_active_color': 'rgba(80, 80, 80, 0.9)',
            'text_color': '#ffffff'
        },
        'Commands': {
            'lock': '',
            'logout': ''
        },
        'Button/lock': {
            'enabled': 'True',
            'label': 'Lock',
            'icon': 'changes-prevent-symbolic',
            'command': 'lock'
        },
        'Button/logout': {
            'enabled': 'True',
            'label': 'Logout',
            'icon': 'system-log-out-symbolic',
            'command': 'logout'
        },
        'Button/reboot': {
            'enabled': 'True',
            'label': 'Reboot',
            'icon': 'system-reboot-symbolic',
            'command': 'reboot'
        },
        'Button/shutdown': {
            'enabled': 'True',
            'label': 'Shutdown',
            'icon': 'system-shutdown-symbolic',
            'command': 'poweroff'
        },
        'Button/suspend': {
            'enabled': 'True',
            'label': 'Suspend',
            'icon': 'weather-clear-night-symbolic',
            'command': 'suspend'
        },
        'Button/hibernate': {
            'enabled': 'True',
            'label': 'Hibernate',
            'icon': 'weather-clear-night-symbolic',
            'command': 'hibernate'
        },
        'Button/cancel': {
            'enabled': 'True',
            'label': 'Cancel',
            'icon': 'window-close-symbolic',
            'command': ''
        }
    })
    
    # Load from config files
    config_paths = [
        Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config')) / 'wlogout.ini',
        Path('/etc/wlogout.ini')
    ]
    
    for path in config_paths:
        if path.exists():
            config.read(path)
    
    return config

def main():
    parser = argparse.ArgumentParser(description="Logout menu for Linux systems")
    parser.add_argument("-r", "--runit", action="store_true", help="Use loginctl (for runit systems)")
    parser.add_argument("-s", "--systemd", action="store_true", help="Use systemctl (for systemd systems)")
    parser.add_argument("-c", "--config", help="Path to custom config file")
    
    args = parser.parse_args()
    
    config = load_config()
    if args.config:
        config.read(args.config)
    
    # Override config with command line args
    if args.runit:
        config['DEFAULT']['use_runit'] = 'True'
    elif args.systemd:
        config['DEFAULT']['use_runit'] = 'False'
    
    # Generate CSS from config
    css = f"""
    * {{
        font-family: 'Sans';
        font-size: 16px;
    }}
    
    window {{
        background-color: {config.get('Layout', 'background_color')};
    }}
    
    .logout-button {{
        color: {config.get('Layout', 'text_color')};
        background-color: {config.get('Layout', 'button_color')};
        border-radius: 10px;
        padding: 20px;
    }}
    
    .logout-button:hover {{
        background-color: {config.get('Layout', 'button_hover_color')};
    }}
    
    .logout-button:active {{
        background-color: {config.get('Layout', 'button_active_color')};
    }}
    
    .logout-button image {{
        color: {config.get('Layout', 'text_color')};
    }}
    
    .logout-button label {{
        color: {config.get('Layout', 'text_color')};
    }}
    """
    
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(css.encode())
    
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    
    win = LogoutMenu(config)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
