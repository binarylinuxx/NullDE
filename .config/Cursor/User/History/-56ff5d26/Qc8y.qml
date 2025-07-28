pragma Singleton
import QtQuick

QtObject {
    // Bar configuration
    readonly property int barHeight: 31
    readonly property int barMargin: 8
    readonly property int barSpacing: 12
    
    // Widget configuration
    readonly property int widgetHeight: 25
    readonly property int widgetRadius: 7
    readonly property int widgetPadding: 10
    
    // Timeouts and intervals
    readonly property int errorTimeout: 5000  // 5 seconds for error detection
    readonly property int notificationTimeout: 5000  // 5 seconds for notifications
    readonly property int osdTimeout: 1000  // 1 second for OSD display
    
    // Screen corner configuration
    readonly property int cornerSize: 20
    readonly property real cornerOpacity: 0.3
    
    // Control panel configuration
    readonly property int controlPanelWidth: 320
    readonly property int controlPanelHeight: 400
    readonly property int controlPanelMargin: 16
    readonly property int controlPanelSpacing: 16
    
    // Font configuration
    readonly property string fontFamily: "Jetbrains Mono"
    readonly property int fontSizeSmall: 12
    readonly property int fontSizeNormal: 16
    readonly property int fontSizeLarge: 18
    
    // Feature toggles
    readonly property bool enableNotifications: true
    readonly property bool enableScreenCorners: true
    readonly property bool enableErrorHandling: true
    readonly property bool enableLogging: true
    
    // Fallback values
    readonly property int fallbackWidth: 1920
    readonly property int fallbackHeight: 1080
} 