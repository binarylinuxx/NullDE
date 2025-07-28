import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Window {
    id: mainWindow
    width: 300
    height: 100
    visible: true
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"
    
    property var currentNotification: null
    property var notificationQueue: []
    
    // Simple shadow implementation
    Rectangle {
        id: shadow
        anchors.fill: parent
        anchors.margins: -5
        radius: parent.radius + 5
        color: "#80000000"
        z: -1
    }
    
    Rectangle {
        id: mainWindowBox
        anchors.fill: parent
        radius: 10
        color: "#282a36"
        border.color: "#44475a"
        border.width: 1
        
        visible: currentNotification !== null
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 5
            
            RowLayout {
                Layout.fillWidth: true
                
                Rectangle {
                    id: titleBox
                    Layout.fillWidth: true
                    height: 20
                    color: "transparent"
                    
                    Text {
                        text: currentNotification ? currentNotification.appName : ""
                        color: "#f8f8f2"
                        font.bold: true
                        elide: Text.ElideRight
                    }
                }
                
                Button {
                    id: closeButton
                    text: "×"
                    flat: true
                    onClicked: updateCurrentNotification()
                    
                    background: Rectangle {
                        color: "transparent"
                    }
                    
                    contentItem: Text {
                        text: closeButton.text
                        color: "#f8f8f2"
                        font.pixelSize: 16
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
            
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 10
                
                Rectangle {
                    id: iconBox
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                    color: "transparent"
                    
                    Image {
                        id: appIcon
                        source: currentNotification ? (currentNotification.appIcon || "qrc:/default-icon.png") : ""
                        sourceSize.width: 32
                        sourceSize.height: 32
                        fillMode: Image.PreserveAspectFit
                        visible: status === Image.Ready
                        
                        onStatusChanged: {
                            if (status === Image.Error) {
                                source = "qrc:/default-icon.png"
                            }
                        }
                    }
                }
                
                Rectangle {
                    id: mainTextBox
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "transparent"
                    
                    Text {
                        width: parent.width
                        wrapMode: Text.Wrap
                        text: currentNotification ? (currentNotification.summary + "\n" + currentNotification.body) : ""
                        color: "#f8f8f2"
                    }
                }
            }
        }
    }
    
    // Position at top-right of screen
    x: Screen.desktopAvailableWidth - width - 20
    y: 20
    
    Behavior on opacity {
        NumberAnimation { duration: 200 }
    }
    
    onCurrentNotificationChanged: {
        if (currentNotification) {
            opacity = 1
            show()
        } else {
            opacity = 0
        }
    }
    
    function handleNotification(id, appName, appIcon, summary, body) {
        // Check if this replaces an existing notification
        for (var i = 0; i < notificationQueue.length; i++) {
            if (notificationQueue[i].id === id) {
                notificationQueue[i] = {
                    id: id,
                    appName: appName,
                    appIcon: appIcon,
                    summary: summary,
                    body: body,
                    timestamp: new Date()
                };
                updateCurrentNotification();
                return;
            }
        }
        
        // Add new notification
        notificationQueue.push({
            id: id,
            appName: appName,
            appIcon: appIcon,
            summary: summary,
            body: body,
            timestamp: new Date()
        });
        
        if (!currentNotification) {
            updateCurrentNotification();
        }
    }
    
    function updateCurrentNotification() {
        if (notificationQueue.length > 0) {
            currentNotification = notificationQueue.shift();
            notificationTimer.restart();
        } else {
            currentNotification = null;
            mainWindow.hide();
        }
    }
    
    Timer {
        id: notificationTimer
        interval: 5000
        running: false
        repeat: false
        onTriggered: updateCurrentNotification()
    }
}
