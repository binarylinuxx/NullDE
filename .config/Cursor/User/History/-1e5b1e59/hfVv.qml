import QtQuick 2.15
import Quickshell
import Quickshell.Services.Notifications

Item {
    id: root

    NotificationServer {
        id: notificationServer
        onNotificationAdded: {
            notificationPopupComponent.createObject(root, { "notification": notification });
        }
    }

    Component {
        id: notificationPopupComponent

        FloatingWindow {
            width: 320
            height: 80
            visible: true
            flags: Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint

            Rectangle {
                anchors.fill: parent
                color: "#222"
                radius: 8
                border.color: "#555"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 4

                    Text {
                        text: notification.summary
                        color: "white"
                        font.bold: true
                        font.pixelSize: 16
                    }
                    Text {
                        text: notification.body
                        color: "#ccc"
                        font.pixelSize: 13
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Timer {
                interval: notification.timeout > 0 ? notification.timeout : 5000
                running: true
                onTriggered: parent.destroy()
            }

            property var notification
        }
    }
} 