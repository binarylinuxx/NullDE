import QtQuick
import QtQuick.Controls
import Quickshell
import "./widgets" as Widgets
import "./"     

PanelWindow {
    height: 31
    //color: Colors.background
    width: parent ? parent.width : 1920  // Fallback width if parent is unavailable
    color: "#210e0b"

    anchors {
        bottom: true;
        left: true;
        right: true;
    }

    // Right side widgets with better spacing
    Widgets.Clock {
        id: clockWidget
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: 8
    }

    Widgets.Audio {
        id: audioWidget
        anchors.right: clockWidget.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: 12
    }

    Widgets.KbLang {
        id: kbLangWidget
        anchors.right: audioWidget.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: 12
    }

    // Center widget
    Widgets.Workspaces {
        id: workspacesWidget
        anchors.centerIn: parent
        anchors.rightMargin: 400
    }

    // Left side widget
    Widgets.ActiveWindow {
        id: activeWindowWidget
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 8
    }

    // Add error handling for parent width
    Component.onCompleted: {
        if (!parent) {
            console.warn("Bar: No parent detected, using fallback width")
        } else {
            console.log("Bar: Initialized with width:", width)
        }
    }
}
