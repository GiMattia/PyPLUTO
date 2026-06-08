"""Main GUI module."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from pyPLUTO.gui.main_window import PyPLUTOApp


def main() -> None:
    """Launch the PyPLUTO GUI application."""
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code="PLUTO")
    window.resize(1150, 720)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
