import sys

from PySide6.QtWidgets import QApplication

from .main_window import PyPLUTOApp


def main() -> None:
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code="PLUTO")
    window.resize(1150, 720)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
