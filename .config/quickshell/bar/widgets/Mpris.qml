import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Services.Mpris

Item {
    id: mprisWidget
    height: 25

    Rectangle {
        id: background
        anchors.fill: parent
        color: "#4c332f"
        radius: 7

        Label {
            id: titleLabel
            anchors.centerIn: parent
            text: {
                if (!Mpris.currentPlayer) return "No Player"
                let artist = Mpris.currentPlayer.trackArtists.join(", ") || "Unknown Artist"
                let title = Mpris.currentPlayer.trackTitle || "Unknown Title"
                // Clean up " - YouTube Music" from the title
                title = title.replace(/ - YouTube Music$/, "")
                return `Author: ${artist} Song: ${title}`
            }
            color: "white"
            font.pixelSize: 16
            font.bold: true
            font.family: "Jetbrains Mono, sans-serif"
        }
    }

    width: titleLabel.implicitWidth + 12

    Timer {
        interval: 1000 // Update every 1 second
        running: true
        repeat: true
        onTriggered: {
            // Force re-evaluation of the Label's text binding
            titleLabel.text = Qt.binding(function() {
                if (!Mpris.currentPlayer) return "No Player"
                let artist = Mpris.currentPlayer.trackArtists.join(", ") || "Unknown Artist"
                let title = Mpris.currentPlayer.trackTitle || "Unknown Title"
                title = title.replace(/ - YouTube Music$/, "")
                return `Author: ${artist} Song: ${title}`
            })
        }
    }
}
