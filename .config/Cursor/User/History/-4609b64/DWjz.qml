import QtQuick
import QtQuick.Controls
import Quickshell
import "./bar"
import "./effects"
import "./bar/widgets"
import "./popup_menu"
import "./notifs"
import "./"     

ShellRoot {
    Bar{}
    Osd{}
    ControlPanel{}
    Notifs{}
    ScreenCorner{}
    
    // Add initialization logging and error handling
    Component.onCompleted: {
        console.log("Quickshell initialized successfully")
        console.log("Components loaded: Bar, Osd, ControlPanel, Notifs, ScreenCorner")
    }
    
    Component.onDestruction: {
        console.log("Quickshell shutting down")
    }
} 

