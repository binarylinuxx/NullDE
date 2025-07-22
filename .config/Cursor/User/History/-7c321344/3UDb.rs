use gtk4::prelude::*;
use gtk4::{Application, ApplicationWindow, Box as GtkBox, Orientation, Notebook, Label};
use ini::Ini;
use std::path::Path;

fn main() {
    let app = Application::builder()
        .application_id("com.github.binarylinuxx.hyprland-settings-rust")
        .build();

    app.connect_activate(build_ui);
    app.run();
}

fn build_ui(app: &Application) {
    let window = ApplicationWindow::builder()
        .application(app)
        .title("Hyprland Settings (Rust)")
        .default_width(800)
        .default_height(600)
        .build();

    let notebook = Notebook::new();

    // Desktop tab
    let desktop_box = GtkBox::new(Orientation::Vertical, 12);
    desktop_box.append(&Label::new(Some("[Desktop section placeholder]")));
    notebook.append_page(&desktop_box, Some(&Label::new(Some("Desktop"))));

    // Screen tab
    let screen_box = GtkBox::new(Orientation::Vertical, 12);
    screen_box.append(&Label::new(Some("[Screen section placeholder]")));
    notebook.append_page(&screen_box, Some(&Label::new(Some("Screen"))));

    // Audio tab
    let audio_box = GtkBox::new(Orientation::Vertical, 12);
    audio_box.append(&Label::new(Some("[Audio section placeholder]")));
    notebook.append_page(&audio_box, Some(&Label::new(Some("Audio"))));

    // System Info tab
    let sysinfo_box = GtkBox::new(Orientation::Vertical, 12);
    sysinfo_box.append(&Label::new(Some("[System Info section placeholder]")));
    notebook.append_page(&sysinfo_box, Some(&Label::new(Some("System Info"))));

    window.set_child(Some(&notebook));
    window.present();
}
