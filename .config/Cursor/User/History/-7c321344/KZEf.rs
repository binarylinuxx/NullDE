use gtk4::prelude::*;
use gtk4::{Application, ApplicationWindow, Label};
use ini::Ini;
use std::path::Path;

fn main() {
    // Load config example (will look for ~/.config/hyprsettings/config.ini)
    let config_path = dirs::home_dir()
        .map(|h| h.join(".config/hyprsettings/config.ini"))
        .unwrap_or_else(|| Path::new("config.ini").to_path_buf());
    let config = Ini::load_from_file(&config_path).ok();

    let app = Application::builder()
        .application_id("com.github.binarylinuxx.hyprland-settings-rust")
        .build();

    app.connect_activate(move |app| {
        let window = ApplicationWindow::builder()
            .application(app)
            .title("Hyprland Settings (Rust)")
            .default_width(800)
            .default_height(600)
            .build();

        let label = if let Some(conf) = &config {
            let wallpaper = conf.section(Some("Desk")).and_then(|s| s.get("wallpaper")).unwrap_or("(none)");
            Label::new(Some(&format!("Config loaded! Wallpaper: {}", wallpaper)))
        } else {
            Label::new(Some("No config found or failed to load."))
        };

        window.set_child(Some(&label));
        window.present();
    });

    app.run();
}
