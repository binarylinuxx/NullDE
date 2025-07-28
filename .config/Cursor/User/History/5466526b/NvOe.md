# grs

A custom Rust GTK4 shell for building Hyprland bars/desktops using gtk4-layer-shell.

## Features
- GTK4 + Layer Shell integration
- Minimal base for custom bar/desktop widgets

## Build & Run

```sh
cd grs
cargo run
```

## Requirements
- Rust toolchain
- GTK4 development libraries
- Hyprland (for layer shell usage)

## Configuration

The application loads its configuration from `~/.config/grs/config.ron` in [RON](https://github.com/ron-rs/ron) format.

### Example config.ron
```ron
(
    bar_height: Some(50),
    bar_width: Some(800),
    bar_position: Some("top"),
)
```

If the file is missing or invalid, defaults are used.

---
This is a minimal base. Extend it to add widgets, custom layouts, and more! 