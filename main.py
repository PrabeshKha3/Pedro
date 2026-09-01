import sys
from PyQt6.QtWidgets import QApplication
from Webcam import Webcam

def main():
    app = QApplication(sys.argv)
    window = Webcam()
    window.show()
    sys.exit(app.exec())
    window.closeEvent()

if __name__ == "__main__":
    main()