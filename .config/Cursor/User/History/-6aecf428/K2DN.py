import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
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