import sys

from main_window import PyPLUTOApp
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code="PLUTO")
    window.resize(1150, 720)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
