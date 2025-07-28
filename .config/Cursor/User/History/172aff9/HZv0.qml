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
    property bool isError: false

    Rectangle {
        anchors.fill: parent
        color: isError ? "#93000a" : "#4c332f"  // Error color or normal color
        radius: 7
        Label {
            id: layoutLabel
            anchors.centerIn: parent
            text: isError ? "?" : currentLayout
            color: "white"
            font.pixelSize: 16
            font.bold: true
            font.family: "Jetbrains Mono"
        }
    }

    width: layoutLabel.implicitWidth + 10

    Process {
        id: layoutProc
        command: ["sh", "-c", "hyprctl devices 2>/dev/null | grep 'active keymap' | sed -n '4p' | sed 's/.*active keymap: //'"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                if (data && data.trim()) {
                    currentLayout = data.trim().includes("Russian") ? "RU" : "EN"
                    isError = false
                } else {
                    isError = true
                    console.warn("No keyboard layout data received")
                }
            }
        }
    }

    // Timer to detect if process is taking too long (error detection)
    Timer {
        id: errorTimer
        interval: 5000  // 5 seconds timeout
        repeat: false
        onTriggered: {
            if (layoutProc.running) {
                isError = true
                console.warn("Keyboard layout detection timed out")
            }
        }
    }

    Component.onCompleted: {
        // Подключаемся к событиям Hyprland для мгновенного обновления
        Hyprland.rawEvent.connect(updateLayout)
        errorTimer.start()
    }

    function updateLayout() {
        layoutProc.running = true
        errorTimer.restart()
    }
}
