import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    width: 1920
    height: 32
    color: "#222222"
    Row {
        anchors.fill: parent
        spacing: 10
        Text {
            text: Qt.formatDateTime(new Date(), "hh:mm:ss")
            color: "white"
            font.pixelSize: 20
        }
    }
} 