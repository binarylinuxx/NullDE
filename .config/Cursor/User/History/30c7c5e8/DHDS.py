import gi
import sys

gi.require_version('Gtk', '4.0')
gi.require_version('GtkLayerShell', '0')
from gi.repository import Gtk, GtkLayerShell  # type: ignore


def main():
    # Create main window
    window = Gtk.Window()
    window.set_title("Hyprland Dock Panel")
    window.set_default_size(600, 48)
    window.set_resizable(False)

    # Init layer shell
    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_layer(window, GtkLayerShell.Layer.BOTTOM)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.BOTTOM, True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT, True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.RIGHT, True)
    GtkLayerShell.set_margin(window, GtkLayerShell.Edge.BOTTOM, 0)
    GtkLayerShell.auto_exclusive_zone_enable(window)

    # Create a horizontal box for dock buttons
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    box.set_margin_top(6)
    box.set_margin_bottom(6)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # Sample buttons
    for label in ["Terminal", "Files", "Web", "Settings"]:
        btn = Gtk.Button(label=label)
        box.append(btn)

    window.set_child(box)
    window.connect("close-request", lambda w: Gtk.main_quit())
    window.present()
    Gtk.main()

if __name__ == "__main__":
    main() 