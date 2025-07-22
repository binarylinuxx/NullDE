import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Hyprland

Item {
    id: root
    height: 30
    
    Rectangle {
        id: container
        width: workspaceRow.width + 4
        height: 25
        radius: 15
        color: "#4c332f"
        border.color: "#45475a"
        border.width: 0
        
        // Center the container in the parent
        anchors.centerIn: parent
        
        Row {
            id: workspaceRow
            anchors.centerIn: parent
            spacing: 2
            
            Repeater {
                model: Hyprland.workspaces
                Rectangle {
                    width: modelData.active ? 21 : 21
                    height: 21
                    radius: 15
                    color: modelData.active ? "#ff5541" : "transparent"
                    border.color: modelData.hasFullscreen ? "#f38ba8" : "transparent"
                    border.width: modelData.hasFullscreen ? 2 : 0
                    
                    Behavior on width {
                        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                    }
                    
                    Text {
                        anchors.centerIn: parent
                        text: modelData.id
                        color: modelData.active ? "white" : "black"
                        font.pixelSize: 14
                        font.bold: true
                        font.family: "JetBrains Mono"
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: modelData.activate()
                    }
                }
            }
        }
    }
}
