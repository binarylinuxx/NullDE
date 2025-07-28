use gtk4::prelude::*;
use gtk4::{Application, ApplicationWindow};
use gtk4_layer_shell::LayerShell;

fn main() {
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
