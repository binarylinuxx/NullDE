import QtQuick 2.15
import QtQuick.Controls 2.15
import Quickshell
import Quickshell.Hyprland

PanelWindow {
    // Access Hyprland monitor information
    width: 1920
    height: 1049
    color: "transparent"

    // Bottom-left corner
    Rectangle {
        width: 20
        height: 20
        radius: 10
        color: "black"
        anchors.bottom: parent.bottom
        anchors.left: parent.left
    }

    // Bottom-right corner
    Rectangle {
        width: 20
        height: 20
        radius: 10
        color: "black"
        anchors.bottom: parent.bottom
        anchors.right: parent.right
    }
}

