import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import threading
import time
import uuid

class Notification:
    def __init__(self, summary, body, icon, actions, hints):
        self.id = str(uuid.uuid4())
        self.summary = summary
        self.body = body
        self.icon = icon
        self.actions = actions
        self.hints = hints
        self.timer = None

notifications = []

def remove_notification(notif_id):
    global notifications
    notifications = [n for n in notifications if n.id != notif_id]
    print_state()

def add_object(notif):
    notifications.insert(0, notif)
    
    # Auto-remove after timeout unless persistent
    if notif.timer and notif.timer.is_alive():
        notif.timer.cancel()
    
    timeout = 10  # Default timeout
    if 'x-canonical-private-synchronous' in notif.hints:
        timeout = 30  # Longer timeout for important notifications
    
    notif.timer = threading.Timer(timeout, remove_notification, args=(notif.id,))
    notif.timer.start()
    
    print_state()

def print_state():
    notif_string = ""
    for item in notifications:
        # Escape single quotes for EWW
        summary_esc = item.summary.replace("'", "&#39;") if item.summary else ''
        body_esc = item.body.replace("'", "&#39;") if item.body else ''
        icon_esc = item.icon.replace("'", "&#39;") if item.icon else ''
        
        action_buttons = ""
        if item.actions:
            for i in range(0, len(item.actions), 2):
                action_id = item.actions[i]
                action_label = item.actions[i+1]
                action_label_esc = action_label.replace("'", "&#39;")
                action_buttons += f"""
                (button :class 'action-btn'
                 :onclick 'dbus-send --session --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.ActionInvoked uint32:0 string:{action_id}'
                 '{action_label_esc}')"""
        
        notif_string += f"""
        (box :class 'notif' :data-id '{item.id}'
          (box :orientation 'horizontal' :space-evenly false
            (image :image-width 80 :image-height 80 :path '{icon_esc or ""}')
            (box :orientation 'vertical' :spacing 5 :hexpand true
              (box :orientation 'horizontal' :space-between true :halign 'fill'
                (label :class 'summary' :wrap true :text '{summary_esc or ""}')
                (button :class 'close-btn' 
                 :onclick 'dbus-send --session --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.CloseNotification uint32:0'
                 "×")
              )
              (label :class 'body' :wrap true :text '{body_esc or ""}')
              (box :orientation 'horizontal' :class 'actions' :spacing 5
                {action_buttons}
              )
            )
          )
        )"""

class NotificationServer(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.freedesktop.Notifications', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/Notifications')
        self.notification_id = 0

    @dbus.service.method('org.freedesktop.Notifications', in_signature='susssasa{ss}i', out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, timeout):
        self.notification_id += 1
        add_object(Notification(summary, body, app_icon, actions, hints))
        return self.notification_id

    @dbus.service.method('org.freedesktop.Notifications', out_signature='ssss')
    def GetServerInformation(self):
        return ("EWW Notification Server", "EWW", "1.0", "1.2")
    
    @dbus.service.method('org.freedesktop.Notifications', in_signature='u')
    def CloseNotification(self, id):
        remove_notification(id)
    
    @dbus.service.signal('org.freedesktop.Notifications', signature='us')
    def ActionInvoked(self, id, action_key):
        pass

DBusGMainLoop(set_as_default=True)

if __name__ == '__main__':
    server = NotificationServer()
    mainloop = GLib.MainLoop()
    mainloop.run()
