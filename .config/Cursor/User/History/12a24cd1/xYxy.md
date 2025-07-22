# QtBar: Customizable Qt Panel for Hyprland

A Python + Qt (PySide6) panel for Hyprland, configurable via QML at `~/.config/qtbar/config.qml`.

## Features
- Customizable panel using QML
- Easily extensible with new widgets
- Integrates with Hyprland (planned)

## Installation

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Create config directory and sample config:**
   ```sh
   mkdir -p ~/.config/qtbar
   cp panel.qml ~/.config/qtbar/config.qml
   # Or create your own config.qml
   ```

3. **Run the panel:**
   ```sh
   python main.py
   ```

## Configuration
Edit `~/.config/qtbar/config.qml` to customize the panel layout and widgets.

## Example QML Config
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    width: 1920
    height: 32
    color: "#222222"
    Row {
        anchors.fill: parent
        spacing: 10
        Text {
            text: Qt.formatDateTime(new Date(), "hh:mm:ss")
            color: "white"
            font.pixelSize: 20
        }
    }
}
```

## Roadmap
- Add more widgets (workspaces, system info, etc.)
- Hyprland integration
- Hot-reload config 