import QtQuick
import QtQuick.Controls
import Quickshell
import "./widgets" as Widgets
import "./"     

PanelWindow {
    height: 30
    width: parent ? parent.width : 1920  // Fallback width if parent is unavailable
    color: Colors.background

    anchors {
        top: true;
        left: true;
        right: true;
    }

    Widgets.Clock {
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: 3
    }

    Widgets.Audio {
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: 85
    }

    Widgets.Workspaces {
        anchors.centerIn: parent
        anchors.rightMargin: 400
    }

    Widgets.ActiveWindow {
        anchors.left: parent.left
        anchors.leftMargin: 4
    }
}
