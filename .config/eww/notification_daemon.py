#!/usr/bin/env python3
import dbus
import dbus.service
import json
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class Notification:
    def __init__(self, id, app_name, summary, body, icon, urgency, timeout):
        self.id = id
        self.app_name = app_name
        self.summary = summary
        self.body = body
        self.icon = icon
        self.urgency = urgency  # 0=low, 1=normal, 2=critical
        self.timestamp = int(time.time())
        self.timeout = timeout if timeout > 0 else 5000  # Default 5s if persistent

class NotificationServer(dbus.service.Object):
    def __init__(self):
        self.notifications = []
        self.last_id = 0
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName('org.freedesktop.Notifications', bus=bus)
        super().__init__(bus_name, '/org/freedesktop/Notifications')

    @dbus.service.method('org.freedesktop.Notifications', in_signature='susssasa{ss}i', out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, timeout):
        self.last_id += 1
        urgency = hints.get('urgency', 1) if isinstance(hints, dict) else 1
        notif = Notification(self.last_id, app_name, summary, body, app_icon, urgency, timeout)
        
        if replaces_id > 0:
            self.notifications = [n for n in self.notifications if n.id != replaces_id]
        
        self.notifications.insert(0, notif)
        self._emit_update()
        return notif.id

    @dbus.service.method('org.freedesktop.Notifications', in_signature='u', out_signature='')
    def CloseNotification(self, id):
        self.notifications = [n for n in self.notifications if n.id != id]
        self._emit_update()

    def _emit_update(self):
        """Outputs minimal structured data for EWW to process"""
        print(json.dumps([{
            'id': n.id,
            'app': n.app_name,
            'summary': n.summary,
            'body': n.body,
            'icon': n.icon or '',
            'urgency': n.urgency,
            'time': n.timestamp
        } for n in self.notifications]), flush=True)

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    server = NotificationServer()
    GLib.MainLoop().run()
