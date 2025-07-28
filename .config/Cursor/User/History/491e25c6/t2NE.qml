import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Services.Pipewire

Item {
    id: audioWidget
    height: 25

    // Track the default audio sink
    PwObjectTracker {
        objects: [Pipewire.defaultAudioSink]
    }

    // Volume property (0-1 range)
    property real volume: Pipewire.defaultAudioSink?.audio.volume ?? 0
    property var controlPanel // This will reference the ControlPanel

    Rectangle {
        id: audioBackground
        anchors.fill: parent
        color: Colors.surface_container_high // was "#4c332f"
        radius: 7

        Row {
            anchors.centerIn: parent
            spacing: 5

            Text {
                id: volumeIcon
                text: {
                    if (volume === 0) return "\uf026";  // Muted
                    if (volume < 0.6) return "\uf027"; // Low
                    return "\uf028";                    // Full
                }
                color: Colors.on_surface // was "white"
                font.pixelSize: 16
                font.family: "JetbrainsMono Nerd Font, monospace" // fallback to monospace
            }

            Text {
                id: volumeLabel
                text: Math.round(volume * 100) + "%"
                color: Colors.on_surface // was "white"
                font.pixelSize: 16
                font.bold: true
                font.family: "Jetbrains Mono, monospace" // fallback to monospace
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                if (controlPanel) {
                    controlPanel.toggle()
                }
            }
        }
    }

    width: volumeIcon.implicitWidth + volumeLabel.implicitWidth + 20

    Connections {
        target: Pipewire.defaultAudioSink?.audio
        function onVolumeChanged() {
            volume = Pipewire.defaultAudioSink.audio.volume
        }
    }
}
