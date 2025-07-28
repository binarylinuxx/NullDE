import QtQuick 2.0
import QtQuick.Controls 2.15
import Quickshell.Io
import Quickshell.Hyprland

Item {
    id: layoutWidget
    height: 25
    anchors.right: parent.right
    anchors.rightMargin: 10
    anchors.verticalCenter: parent.verticalCenter

    property string currentLayout: "EN"

    Rectangle {
        anchors.fill: parent
        color: "#4c332f"
        radius: 7
        Label {
            id: layoutLabel
            anchors.centerIn: parent
            text: currentLayout
            color: "white"
            font.pixelSize: 16
            font.bold: true
            font.family: "Jetbrains Mono"
        }
    }

    width: layoutLabel.implicitWidth + 10

    Process {
        id: layoutProc
        command: ["sh", "-c", "hyprctl devices | grep 'active keymap' | sed -n '4p' | sed 's/.*active keymap: //'"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                currentLayout = data.trim().includes("Russian") ? "RU" : "EN"
            }
        }
    }

    Component.onCompleted: {
        // Подключаемся к событиям Hyprland для мгновенного обновления
        Hyprland.rawEvent.connect(updateLayout)
    }

    function updateLayout() {
        layoutProc.running = true
    }
}
