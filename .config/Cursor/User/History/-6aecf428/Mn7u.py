import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from widgets.systeminfo import SystemInfo

def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    # Register Python object for QML
    system_info = SystemInfo()
    engine.rootContext().setContextProperty("SystemInfo", system_info)
    config_path = os.path.expanduser("~/.config/qtbar/config.qml")
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    engine.load(config_path)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 