#!/usr/bin/env python3

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import sys
import os
import requests
from urllib.parse import unquote, urlparse
import base64
from gi.repository import GLib

def get_thumbnail_path(metadata):
    """Extract thumbnail path from metadata and convert to proper file path if needed"""
    if 'mpris:artUrl' not in metadata:
        return None
    
    art_url = metadata['mpris:artUrl']
    if not art_url:
        return None
    
    # Handle URL-encoded paths
    art_url = unquote(art_url)
    
    # Handle file:// URLs
    if art_url.startswith('file://'):
        return urlparse(art_url).path
    
    # Handle base64 encoded album art (Spotify sometimes does this)
    if art_url.startswith('data:image/'):
        try:
            header, encoded = art_url.split(',', 1)
            ext = header.split('/')[1].split(';')[0]
            img_data = base64.b64decode(encoded)
            
            # Create cache directory if it doesn't exist
            cache_dir = os.path.expanduser('~/.cache/eww/mpris_art')
            os.makedirs(cache_dir, exist_ok=True)
            
            # Save to cache file
            cache_file = os.path.join(cache_dir, f"current_art.{ext}")
            with open(cache_file, 'wb') as f:
                f.write(img_data)
            
            return cache_file
        except Exception:
            return None
    
    # Handle web URLs (download and cache)
    if art_url.startswith(('http://', 'https://')):
        try:
            cache_dir = os.path.expanduser('~/.cache/eww/mpris_art')
            os.makedirs(cache_dir, exist_ok=True)
            
            # Get file extension from URL or content type
            ext = 'jpg'
            if '.' in art_url.split('?')[0]:
                ext = art_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                    ext = 'jpg'
            
            cache_file = os.path.join(cache_dir, "current_art." + ext)
            
            # Download the image
            response = requests.get(art_url, stream=True, timeout=2)
            if response.status_code == 200:
                with open(cache_file, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return cache_file
        except Exception:
            return None
    
    return None

def get_mpris_info():
    DBusGMainLoop(set_as_default=True)
    
    try:
        bus = dbus.SessionBus()
        players = [name for name in bus.list_names() if name.startswith('org.mpris.MediaPlayer2.')]
        
        if not players:
            return {
                'PERCENT': '0',
                'DISPLAY_TEXT': 'No media playing',
                'TOOLTIP_TEXT': '',
                'THUMBNAIL_PATH': ''
            }
        
        player = players[0]
        proxy = bus.get_object(player, '/org/mpris/MediaPlayer2')
        properties = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
        metadata = properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        
        # Extract song info
        title = metadata.get('xesam:title', 'Unknown Track')
        artist = metadata.get('xesam:artist', ['Unknown Artist'])[0]
        
        # Calculate progress percentage
        length = metadata.get('mpris:length', 1)  # microseconds
        position = properties.Get('org.mpris.MediaPlayer2.Player', 'Position')
        percent = int((position / length) * 100) if length > 0 else 0
        
        # Format display text
        display_text = f"{title} - {artist}"
        
        # Format tooltip with time info
        pos_sec = position / 1e6
        len_sec = length / 1e6
        tooltip_text = (f"{int(pos_sec // 60)}:{int(pos_sec % 60):02d} / "
                       f"{int(len_sec // 60)}:{int(len_sec % 60):02d}")
        
        # Get thumbnail path
        thumbnail_path = get_thumbnail_path(metadata)
        
        return {
            'PERCENT': str(percent),
            'DISPLAY_TEXT': display_text,
            'TOOLTIP_TEXT': tooltip_text,
            'THUMBNAIL_PATH': thumbnail_path if thumbnail_path else ''
        }
        
    except Exception as e:
        return {
            'PERCENT': '0',
            'DISPLAY_TEXT': 'MPRIS Error',
            'TOOLTIP_TEXT': str(e),
            'THUMBNAIL_PATH': ''
        }

if __name__ == '__main__':
    info = get_mpris_info()
    
    if len(sys.argv) > 1:
        field = sys.argv[1].upper()
        print(info.get(field, ''))
    else:
        for key, value in info.items():
            print(f"{key}: {value}")

def main_loop():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    
    while True:
        try:
            info = get_mpris_info()
            
            # Output all fields if no argument, or specific field if requested
            if len(sys.argv) > 1:
                field = sys.argv[1].upper()
                print(info.get(field, ''))
            else:
                for key, value in info.items():
                    print(f"{key}: {value}")
            
            # Flush output immediately
            sys.stdout.flush()
            
            # Wait for DBus signals or timeout after 1s
            loop = GLib.MainLoop()
            bus.add_signal_receiver(
                lambda: loop.quit(),
                signal_name='PropertiesChanged',
                dbus_interface='org.freedesktop.DBus.Properties'
            )
            
            # Run for max 1 second or until change detected
            GLib.timeout_add_seconds(1, loop.quit)
            loop.run()
            
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            time.sleep(1)

if __name__ == '__main__':
    main_loop()
