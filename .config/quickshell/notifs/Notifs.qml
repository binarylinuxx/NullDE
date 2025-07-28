// NotificationManager.qml
pragma Singleton
import Quickshell
import QtQuick

Singleton {
    id: root
    
    property var notifications: []
    
    function showNotification(title, message, duration = 5000) {
        // Create a new notification
        var notification = notificationComponent.createObject(null, {
            "title": title,
            "message": message,
            "duration": duration
        })
        
        // Position notifications in a stack
        notification.y = 20 + (notifications.length * 90)
        
        // Add to notifications array
        notifications.push(notification)
        
        // Remove after duration
        notification.onHidden.connect(function() {
            var index = notifications.indexOf(notification)
            if (index > -1) {
                notifications.splice(index, 1)
                repositionNotifications()
            }
            notification.destroy()
        })
    }
    
    function repositionNotifications() {
        for (var i = 0; i < notifications.length; i++) {
            notifications[i].y = 20 + (i * 90)
        }
    }
    
    Component {
        id: notificationComponent
        
        FloatingWindow {
            id: notificationWindow
            
            property string title: ""
            property string message: ""
            property int duration: 5000
            
            signal hidden()
            
            width: 300
            height: 80
            visible: true
            
            x: Quickshell.screens[0].width - width - 20
            
            flags: Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
            
            Rectangle {
                anchors.fill: parent
                color: "#2b2b2b"
                radius: 8
                border.color: "#555555"
                border.width: 1
                
                Text {
                    id: titleLabel
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.margins: 10
                    text: notificationWindow.title
                    color: "white"
                    font.bold: true
                    font.pointSize: 12
                }
                
                Text {
                    id: messageLabel
                    anchors.top: titleLabel.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 10
                    text: notificationWindow.message
                    color: "#cccccc"
                    font.pointSize: 10
                    wrapMode: Text.WordWrap
                }
            }
            
            Timer {
                interval: notificationWindow.duration
                running: true
                onTriggered: {
                    notificationWindow.hidden()
                    notificationWindow.visible = false
                }
            }
            
            // Click to dismiss
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    notificationWindow.hidden()
                    notificationWindow.visible = false
                }
            }
        }
    }
}
