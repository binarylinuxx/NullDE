import gi
import datetime

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import html

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
            self.add_message(text, sender="You")
            self.entry.set_text("")

    def add_message(self, text, sender="User"):
        time_str = datetime.datetime.now().strftime("%H:%M")
        message_label = Gtk.Label()
        message_label.set_xalign(0)
        safe_text = html.escape(text)
        message_label.set_markup(f"<b>{sender}</b> [{time_str}]: {safe_text}")
        row = Gtk.ListBoxRow()
        row.add(message_label)
        self.message_listbox.add(row)
        self.message_listbox.show_all()
        adj = self.message_listbox.get_parent().get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

if __name__ == "__main__":
    app = MessengerDemo()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main() 