from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import os

class NotesWindow(QWidget):
    """Ein kleines Pop-out-Notizfenster, das immer im Vordergrund bleibt."""
    
    notes_updated = pyqtSignal(str)  # ✅ Signal für Änderungen

    def __init__(self, training_folder):
        super().__init__()
        self.training_folder = training_folder
        self.notes_file = os.path.join(self.training_folder, "notes.txt")

        self.initUI()
        self.load_notes()

    def initUI(self):
        """Erstellt die GUI für das Notizen-Popout."""
        self.setWindowTitle("Notizen")
        self.setGeometry(100, 100, 300, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)  # ✅ Immer im Vordergrund

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Schreibe hier deine Notizen...")
        self.text_edit.textChanged.connect(self.handle_text_change)  # ✅ Signal senden
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def load_notes(self):
        """Lädt bestehende Notizen, falls vorhanden."""
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r", encoding="utf-8") as file:
                text = file.read()
                self.text_edit.setText(text)
                self.notes_updated.emit(text)  # ✅ Direktes Update beim Laden

    def handle_text_change(self):
        """Speichert die Notizen und sendet ein Signal an das TrainingWindow."""
        text = self.text_edit.toPlainText()
        with open(self.notes_file, "w", encoding="utf-8") as file:
            file.write(text)

        self.notes_updated.emit(text)  # ✅ Signal an TrainingWindow senden
