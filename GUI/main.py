from PyQt6.QtWidgets import QApplication
import sys
from main_window import PyPLUTOApp
import matplotlib.pyplot as plt

def main():
    plt.ion()
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code = "PLUTO")
    window.resize(1065, 645)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
