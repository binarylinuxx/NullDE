import QtQuick
import QtQuick.Controls

Item {
    id: clockWidget
    height: 25

    property string currentTime: new Date().toLocaleTimeString(Qt.locale(), "hh:mmAP")

    Rectangle {
        id: clockBackground
        anchors.fill: parent
        color: "#4c332f"
        radius: 7
        

        Label {
            id: timeLabel
            anchors.centerIn: parent
            text: currentTime
            color: "white"
            font.pixelSize: 16
            font.bold: true
            font.family: "Jetbrains Mono"
        }
    }

    // Dynamically set width based on text width + 7px
    width: timeLabel.implicitWidth + 12

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: parent.currentTime = new Date().toLocaleTimeString(Qt.locale(), "hh:mmAP")
    }
}
