pragma Singleton
import QtQuick 
//
// Qml Colors For Quickshell setup
// Generated with Matugen
//
QtObject {
<* for name, value in colors *>
    readonly property color {{name}}: "{{value.default.hex}}"
<* endfor *>
}
