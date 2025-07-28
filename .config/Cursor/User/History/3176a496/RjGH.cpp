import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: mainWindowBOX
    width: 400
    height: 120
    color: "#222"
    radius: 12
    border.color: "#444"
    border.width: 2

    Row {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Rectangle {
            id: IconBOX
            width: 48; height: 48
            color: "#333"
            radius: 8
            // Icon image can be added here
        }

        Column {
            spacing: 6
            width: parent.width - IconBOX.width - closeButton.width - 48

            Text {
                id: TitleBOX
                text: "Title"
                color: "#fff"
                font.bold: true
                font.pointSize: 16
            }
            Text {
                id: mainTextBox
                text: "Message text goes here."
                color: "#ccc"
                font.pointSize: 13
                wrapMode: Text.Wrap
            }
        }

        Button {
            id: closeButton
            text: "✕"
            width: 32; height: 32
            anchors.verticalCenter: parent.verticalCenter
            onClicked: Qt.quit()
        }
    }
}
