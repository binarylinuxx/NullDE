import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Widgets

PanelWindow {
    id: toplevel

    anchors {
        top: true
        right: true
    }
    
    width: 300
    height: 500
    visible: false  // Should start hidden and be toggled when needed
    color: "transparent"  // Make window transparent and handle background in child item

    // Rectangle for the actual panel with rounded corners
    Rectangle {
        anchors.fill: parent
        color: "#282a36"  // Dracula theme background color
        radius: 10  // Apply rounded corners here instead
        border.color: "#44475a"
        border.width: 1

        // Your panel content goes here
        Text {
            text: "Control Panel"
            color: "white"
            anchors.centerIn: parent
            font.pixelSize: 16
        }
    }

    PopupWindow {
        anchor.window: toplevel
        width: parent.width
        height: parent.height
        visible: parent.visible
    }

    // Function to toggle visibility
    function toggle() {
        visible = !visible
    }
}

