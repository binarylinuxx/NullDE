import QtQuick 2.0
import QtQuick.Controls 2.15
import Quickshell.Io
import Quickshell.Hyprland

Item {
    id: activeWindowWidget
    height: 25
    
    // Position on left side, centered vertically
    anchors.left: parent.left
    anchors.leftMargin: 10
    anchors.verticalCenter: parent.verticalCenter
    
    property int chopLength: 300  // Add configurable chop length
    property string activeWindowTitle: ""
    
    Rectangle {
        id: backgroundRect
        anchors.fill: parent
        color: "#4c332f"
        radius: 7
        
        Label {
            id: titleLabel
            anchors.centerIn: parent
            text: {
                if (!activeWindowTitle || activeWindowTitle === "N/A" || activeWindowTitle === "Na") {
                    return "Desktop"
                }
                var str = activeWindowTitle
                return str.length > chopLength ? str.slice(0, chopLength) + '' : str; 
            }
            color: "white"
            font.pixelSize: 16
            font.bold: true
            font.family: "Jetbrains Mono"
        }
    }
    
    // Dynamically set width based on text width + 12px
    width: titleLabel.implicitWidth + 15
    
    Process {
        id: titleProc
        command: ["sh", "-c", "hyprctl activewindow | grep title: | sed 's/^[^:]*: //'"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                // Filter out N/A and Na values
                if (data && data !== "N/A" && data !== "Na" && data.trim() !== "") {
                    activeWindowTitle = data
                } else {
                    activeWindowTitle = "Desktop"
                }
            }
        }
    }
    
    Component.onCompleted: {
        Hyprland.rawEvent.connect(hyprEvent)
    }
    
    function hyprEvent(e) {
        titleProc.running = true
    }
}