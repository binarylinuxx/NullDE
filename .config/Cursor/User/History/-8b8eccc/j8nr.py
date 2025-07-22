import gi
import datetime

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import html

class Avatar(Gtk.DrawingArea):
    def __init__(self, color, size=36):
        super().__init__()
        self.color = color
        self.size = size
        self.set_size_request(size, size)
        self.connect('draw', self.on_draw)

    def on_draw(self, widget, cr):
        cr.set_source_rgba(*self.color)
        cr.arc(self.size/2, self.size/2, self.size/2, 0, 2*3.1416)
        cr.fill()

class MessengerDemo(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GTK Messenger Demo")
        self.set_default_size(400, 600)
        self.set_border_width(10)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Header
        header = Gtk.HeaderBar(title="Messenger")
        header.set_subtitle("GTK Demo")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        # Message area (scrollable)
        self.message_listbox = Gtk.ListBox()
        self.message_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.message_listbox)
        scrolled_window.set_vexpand(True)
        vbox.pack_start(scrolled_window, True, True, 0)

        # Entry area
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Type a message...")
        self.entry.connect("activate", self.on_send_clicked)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_clicked)
        entry_box.pack_start(self.entry, True, True, 0)
        entry_box.pack_start(send_button, False, False, 0)
        vbox.pack_start(entry_box, False, False, 0)

    def on_send_clicked(self, widget):
        text = self.entry.get_text().strip()
        if text:
            self.add_message(text, sender="You", sent=True)
            self.entry.set_text("")
            # For demo, add a fake reply
            self.add_message("Echo: " + text, sender="Bot", sent=False)

    def add_message(self, text, sender="User", sent=False):
        time_str = datetime.datetime.now().strftime("%H:%M")
        safe_text = html.escape(text)
        # Message bubble
        bubble = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        bubble.set_homogeneous(False)
        name_label = Gtk.Label()
        name_label.set_markup(f"<small><b>{sender}</b> [{time_str}]</small>")
        name_label.set_xalign(0 if not sent else 1)
        name_label.set_justify(Gtk.Justification.LEFT if not sent else Gtk.Justification.RIGHT)
        msg_label = Gtk.Label()
        msg_label.set_markup(f"{safe_text}")
        msg_label.set_xalign(0 if not sent else 1)
        msg_label.set_justify(Gtk.Justification.LEFT if not sent else Gtk.Justification.RIGHT)
        msg_label.set_line_wrap(True)
        # Bubble styling
        bubble_frame = Gtk.Frame()
        bubble_frame.set_shadow_type(Gtk.ShadowType.IN)
        bubble_frame.set_margin_top(2)
        bubble_frame.set_margin_bottom(2)
        bubble_frame.set_margin_start(4)
        bubble_frame.set_margin_end(4)
        bubble_frame.add(msg_label)
        if sent:
            bubble_frame.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.7, 0.9, 1.0, 1.0))
        else:
            bubble_frame.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.9, 0.9, 0.9, 1.0))
        bubble.pack_start(name_label, False, False, 0)
        bubble.pack_start(bubble_frame, False, False, 0)
        # Avatar
        if sent:
            avatar = Avatar((0.2, 0.6, 1.0, 1.0))
        else:
            avatar = Avatar((0.5, 0.5, 0.5, 1.0))
        # Horizontal box for avatar and bubble
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        if sent:
            hbox.pack_end(bubble, False, False, 0)
            hbox.pack_end(avatar, False, False, 0)
        else:
            hbox.pack_start(avatar, False, False, 0)
            hbox.pack_start(bubble, False, False, 0)
        row = Gtk.ListBoxRow()
        row.add(hbox)
        self.message_listbox.add(row)
        self.message_listbox.show_all()
        adj = self.message_listbox.get_parent().get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

if __name__ == "__main__":
    app = MessengerDemo()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main() 