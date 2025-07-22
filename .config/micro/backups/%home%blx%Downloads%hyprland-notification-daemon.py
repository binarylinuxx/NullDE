#!/usr/bin/env python3
import os
import configparser
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NotificationWindow(Gtk.Window):
    def __init__(self, summary, body, icon, urgency, timeout, css_path):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        
        # Create main container
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        frame.set_name('frame')
        self.add(frame)
        
        # Icon
        if icon and os.path.exists(icon):
            image = Gtk.Image.new_from_file(icon)
            frame.pack_start(image, False, False, 5)
        
        # Content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        content.set_name(urgency)
        frame.pack_start(content, True, True, 5)
        
        # Summary
        summary_label = Gtk.Label(label=summary)
        summary_label.set_name('summary')
        summary_label.set_halign(Gtk.Align.START)
        content.pack_start(summary_label, False, False, 2)
        
        # Separator
        separator = Gtk.HSeparator()
        separator.set_name('hs')
        content.pack_start(separator, False, False, 2)
        
        # Body
        body_text = Gtk.TextView()
        body_text.set_name('body')
        body_text.set_editable(False)
        body_text.set_wrap_mode(Gtk.WrapMode.WORD)
        body_text.get_buffer().set_text(body)
        content.pack_start(body_text, True, True, 2)
        
        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(css_path)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Set timeout
        if timeout > 0:
            GLib.timeout_add(timeout, self.destroy)
    
    def do_show(self):
        # Position window in top-right corner
        screen = self.get_screen()
        monitor = screen.get_monitor_geometry(screen.get_primary_monitor())
        self.move(monitor.width - 300 - 10, 10)
        self.set_default_size(300, -1)
        super().show_all()

class NotificationDaemon(dbus.service.Object):
    def __init__(self, config_path, css_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.css_path = css_path
        self.windows = {}
        
        bus_name = dbus.service.BusName(
            'org.freedesktop.Notifications',
            bus=dbus.SessionBus()
        )
        super().__init__(bus_name, '/org/freedesktop/Notifications')
        logger.info("Notification daemon started")
    
    @dbus.service.method(
        'org.freedesktop.Notifications',
        in_signature='susssasa{sv}i',
        out_signature='u'
    )
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, timeout):
        urgency = hints.get('urgency', 1)
        urgency_map = {0: 'low', 1: 'normal', 2: 'critical'}
        urgency_str = urgency_map.get(urgency, 'normal')
        
        # Generate or use provided ID
        nid = replaces_id if replaces_id else int(uuid.uuid4().int & 0xffffffff)
        
        # Create notification window
        window = NotificationWindow(
            summary, body, app_icon, urgency_str, timeout, self.css_path
        )
        window.connect('destroy', self.on_window_destroyed, nid)
        
        # Store window
        if replaces_id in self.windows:
            self.windows[replaces_id].destroy()
        self.windows[nid] = window
        
        window.show()
        logger.info(f"Showing notification {nid}: {summary}")
        return nid
    
    @dbus.service.method(
        'org.freedesktop.Notifications',
        in_signature='u',
        out_signature=''
    )
    def CloseNotification(self, nid):
        if nid in self.windows:
            self.windows[nid].destroy()
            self.NotificationClosed(nid, 3)  # 3 = Closed by call
            logger.info(f"Closed notification {nid}")
    
    @dbus.service.signal(
        'org.freedesktop.Notifications',
        signature='uu'
    )
    def NotificationClosed(self, nid, reason):
        pass
    
    @dbus.service.method(
        'org.freedesktop.Notifications',
        in_signature='',
        out_signature='ssss'
    )
    def GetServerInformation(self):
        return (
            'Hyprland Notification Daemon',
            'xAI',
            '1.0',
            '1.2'
        )
    
    @dbus.service.method(
        'org.freedesktop.Notifications',
        in_signature='',
        out_signature='as'
    )
    def GetCapabilities(self):
        return ['body', 'icon-static', 'persistence']
    
    def on_window_destroyed(self, window, nid):
        if nid in self.windows:
            del self.windows[nid]
            self.NotificationClosed(nid, 1)  # 1 = Expired
            logger.info(f"Notification {nid} expired")

def main():
    # Initialize DBus main loop
    DBusGMainLoop(set_as_default=True)
    
    # Paths for configuration and CSS
    config_dir = os.path.expanduser('~/.config/hypr-notify')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'config.ini')
    css_path = os.path.join(config_dir, 'style.css')
    
    # Create default configuration if it doesn't exist
    if not os.path.exists(config_path):
        config = configparser.ConfigParser()
        config['General'] = {
            'default_timeout': '5000',
            'max_width': '300'
        }
        with open(config_path, 'w') as f:
            config.write(f)
    
    # Create default CSS if it doesn't exist
    if not os.path.exists(css_path):
        css_content = """
#notification {
    background: transparent;
}
#frame {
    background-color: #d4ded8;
    padding: 3px;
    border-radius: 5px;
}
#hs {
    background-color: black;
}
#critical {
    background-color: #ffaeae;
}
#normal {
    background-color: #f0ffec;
}
#low {
    background-color: #bee3c6;
}
#summary {
    padding-left: 5px;
    font-size: 1.2em;
    font-weight: bold;
}
#body {
    font-size: 1em;
    padding: 5px;
}
"""
        with open(css_path, 'w') as f:
            f.write(css_content)
    
    # Start the daemon
    daemon = NotificationDaemon(config_path, css_path)
    
    # Run the main loop
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
        logger.info("Notification daemon stopped")

if __name__ == '__main__':
    main()