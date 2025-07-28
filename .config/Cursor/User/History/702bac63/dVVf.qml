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

    Widgets.KbLang {
    	anchors.right: parent.right
    	anchors.verticalCenter: parent.verticalCenter
    	anchors.rightMargin: 148
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
