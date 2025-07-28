import QtQuick 2.15
import QtQuick.Controls 2.15
import Quickshell
import Quickshell.Hyprland

PanelWindow {
    id: screenCorner
    
    // Use dynamic screen dimensions with fallback
    width: Quickshell.screens && Quickshell.screens.length > 0 ? Quickshell.screens[0].width : 1920
    height: Quickshell.screens && Quickshell.screens.length > 0 ? Quickshell.screens[0].height : 1080
    color: "transparent"

    // Bottom-left corner
    Rectangle {
        width: 20
        height: 20
        radius: 10
        color: "black"
        opacity: 0.3
        anchors.bottom: parent.bottom
        anchors.left: parent.left
    }

    // Bottom-right corner
    Rectangle {
        width: 20
        height: 20
        radius: 10
        color: "black"
        opacity: 0.3
        anchors.bottom: parent.bottom
        anchors.right: parent.right
    }

    // Add error handling for screen detection
    Component.onCompleted: {
        if (!Quickshell.screens || Quickshell.screens.length === 0) {
            console.warn("No screens detected, using fallback dimensions")
        } else {
            console.log("ScreenCorner initialized with screen:", Quickshell.screens[0].width + "x" + Quickshell.screens[0].height)
        }
    }
}

