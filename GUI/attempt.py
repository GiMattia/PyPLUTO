from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFrame
import sys

class ExpandableBox(QWidget):
    def __init__(self, title=""):
        super().__init__()

        # Layout principale del box espandibile
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Pulsante di intestazione per espandere/comprimere
        self.header_button = QPushButton(title)
        self.header_button.setCheckable(True)
        self.header_button.setStyleSheet("text-align: left; font-weight: bold;")
        self.header_button.clicked.connect(self.toggle_content)
        main_layout.addWidget(self.header_button)

        # Frame contenente il contenuto che si espande/comprime
        self.content_area = QFrame()
        self.content_area.setVisible(False)  # Inizialmente nascosto
        self.content_area.setStyleSheet("background-color: #f0f0f0;")
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area)

    def toggle_content(self):
        # Cambia visibilità dell'area di contenuto
        self.content_area.setVisible(self.header_button.isChecked())

    def add_widget(self, widget):
        # Aggiunge widget al contenuto espandibile
        self.content_layout.addWidget(widget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Layout principale e widget centrale
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Box espandibile con elementi interni
        expandable_box = ExpandableBox("Mostra opzioni")
        expandable_box.add_widget(QLabel("Opzione 1"))
        expandable_box.add_widget(QLabel("Opzione 2"))
        expandable_box.add_widget(QLabel("Opzione 3"))

        # Aggiunge il box espandibile al layout principale
        main_layout.addWidget(expandable_box)

# Configurazione dell'applicazione
app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle("Box Espandibile in PyQt6")
window.resize(300, 200)
window.show()

# Avvio dell'applicazione
sys.exit(app.exec())
