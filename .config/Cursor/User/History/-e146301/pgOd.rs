use gtk4::prelude::*;
use gtk4::{Application, ApplicationWindow};
use gtk4_layer_shell::LayerShell;
use std::fs;
use std::path::PathBuf;
use ron::de::from_str;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct Config {
    // Example config options
    bar_height: Option<i32>,
    bar_width: Option<i32>,
    bar_position: Option<String>,
}

fn load_config() -> Option<Config> {
    let mut config_path = dirs::home_dir()?;
    config_path.push(".config/grs/config.ron");
    let config_str = fs::read_to_string(config_path).ok()?;
    from_str(&config_str).ok()
}

fn main() {
    let config = load_config();
    if let Some(cfg) = &config {
        println!("Loaded config: {:?}", cfg);
    } else {
        println!("No config loaded, using defaults");
    }
    // Initialize GTK application
    let app = Application::builder()
        .application_id("com.example.grs")
        .build();

    app.connect_activate(|app| {
        // Create the main window
        let window = ApplicationWindow::builder()
            .application(app)
            .title("GRS Shell")
            .default_width(800)
            .default_height(50)
            .build();

        // Initialize layer shell for the window
        gtk4_layer_shell::init_for_window(&window);
        gtk4_layer_shell::set_layer(&window, gtk4_layer_shell::Layer::Top);
        gtk4_layer_shell::auto_exclusive_zone_enable(&window);

        window.show();
    });

    app.run();
}
