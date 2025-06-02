import sys
from PyQt5.QtWidgets import QApplication
from blocker.gui import BlockerWindow

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Allow running in system tray
    window = BlockerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
