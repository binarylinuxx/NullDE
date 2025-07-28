import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Widgets
import Quickshell.Services.Pipewire

PanelWindow {
    id: toplevel

    anchors {
        top: true
        right: true
    }
    
    width: 320
    height: 400
    visible: false
    color: "transparent"

    Rectangle {
        anchors.fill: parent
        color: "#282a36"
        radius: 10
        border.color: "#44475a"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 16

            // Header
            Text {
                text: "Control Panel"
                color: "white"
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }

            // Volume Control
            Column {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: "Volume"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                }

                Row {
                    spacing: 8
                    width: parent.width

                    Text {
                        text: "🔊"
                        color: "white"
                        font.pixelSize: 16
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Slider {
                        id: volumeSlider
                        width: parent.width - 40
                        from: 0
                        to: 1
                        value: Pipewire.defaultAudioSink?.audio.volume ?? 0
                        onValueChanged: {
                            if (Pipewire.defaultAudioSink?.audio) {
                                Pipewire.defaultAudioSink.audio.volume = value
                            }
                        }
                    }

                    Text {
                        text: Math.round((Pipewire.defaultAudioSink?.audio.volume ?? 0) * 100) + "%"
                        color: "white"
                        font.pixelSize: 12
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }

            // Brightness Control (placeholder)
            Column {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: "Brightness"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                }

                Row {
                    spacing: 8
                    width: parent.width

                    Text {
                        text: "☀️"
                        color: "white"
                        font.pixelSize: 16
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Slider {
                        id: brightnessSlider
                        width: parent.width - 40
                        from: 0
                        to: 1
                        value: 0.5
                        enabled: false
                    }

                    Text {
                        text: "50%"
                        color: "#888"
                        font.pixelSize: 12
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }

            // Spacer to push content to top
            Item {
                Layout.fillHeight: true
            }

            // Close button
            Button {
                text: "Close"
                Layout.alignment: Qt.AlignHCenter
                onClicked: toplevel.visible = false
            }
        }
    }

    PopupWindow {
        anchor.window: toplevel
        width: parent.width
        height: parent.height
        visible: parent.visible
    }

    function toggle() {
        visible = !visible
    }
}

