import base64
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QHeaderView, QToolBar, QAction, QTextEdit, QFontComboBox, QSpinBox, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QMenu, QAction, QMessageBox, QMenuBar
from PyQt5.QtGui import QPixmap, QFont, QTextCharFormat
from PyQt5.QtCore import Qt
import requests

from gui.notes_window import NotesWindow
from gui.akte_window import AkteWindow
from core.trainee_manager import TraineeManager
from gui.progress_window import ProgressWindow
from core import server_uploader
from core import screenshot_manager


class TrainingWindow(QMainWindow):
    def __init__(self, trainee_name, training_name, training_date, training_id=None):
        super().__init__()
        
        self.trainee_name = trainee_name
        self.training_name = training_name
        print("trainingname", training_name)
        print("Self", self.training_name)
        self.training_date = training_date
        self.training_id = training_id

        self.server_uploader = None

        self.trainee_manager = TraineeManager()
        self.training_folder = self.trainee_manager.get_training_folder(trainee_name, training_name)

        self.screenshot_manager = screenshot_manager.ScreenshotManager(trainee_name, training_name, self, self.update_screenshot_list)
        
        self.initUI()
        self.screenshot_manager.start_watching()

    def initUI(self):
        self.setWindowTitle(f"Trainee Manager - Training {self.training_name}")
        self.setGeometry(200, 200, 900, 600)

        # **🔹 Menüleiste hinzufügen**
        menubar = self.menuBar()
        
        # **🔹 Menü: Training**
        training_menu = menubar.addMenu("Training")
        
        save_action = QAction("Speichern", self)
        save_action.triggered.connect(self.save_all_data)
        training_menu.addAction(save_action)

        write_akte_action = QAction("Akte schreiben", self)
        write_akte_action.triggered.connect(self.open_akte_window)
        training_menu.addAction(write_akte_action)

        end_action = QAction("Beenden", self)
        end_action.triggered.connect(self.end_training)
        training_menu.addAction(end_action)

        # **🔹 Menü: Debrief**
        debrief_menu = menubar.addMenu("Debrief")
        
        start_debrief_action = QAction("Debrief starten", self)
        start_debrief_action.triggered.connect(self.start_debrief)
        debrief_menu.addAction(start_debrief_action)

        # **🔹 Menü: Verwaltung**
        manage_menu = menubar.addMenu("Verwaltung")

        open_trainee_action = QAction("Trainee Verwaltung öffnen", self)
        open_trainee_action.triggered.connect(self.open_trainee_window)
        manage_menu.addAction(open_trainee_action)

        window_menu = menubar.addMenu("Fenster")

        notes_popout_action = QAction("Notiz-Popout", self)
        notes_popout_action.triggered.connect(self.open_notes_window)
        window_menu.addAction(notes_popout_action)

       # **🔹 Hauptlayout (vertikal) → Oben Notizen, unten Screenshots**
        main_layout = QVBoxLayout()

        # **🔹 Toolbar für Formatierung**
        self.toolbar = QToolBar("Text-Formatierung")

        # **Fett**
        self.bold_action = QAction("𝐁", self)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.toolbar.addAction(self.bold_action)

        # **Kursiv**
        self.italic_action = QAction("𝑰", self)
        self.italic_action.triggered.connect(self.toggle_italic)
        self.toolbar.addAction(self.italic_action)

        # **Unterstrichen**
        self.underline_action = QAction("𝐔", self)
        self.underline_action.triggered.connect(self.toggle_underline)
        self.toolbar.addAction(self.underline_action)

        # **Schriftart wählen**
        self.font_selector = QFontComboBox()
        self.font_selector.currentFontChanged.connect(self.change_font)
        self.toolbar.addWidget(self.font_selector)

        # **Schriftgröße**
        self.font_size_selector = QSpinBox()
        self.font_size_selector.setValue(12)
        self.font_size_selector.valueChanged.connect(self.change_font_size)
        self.toolbar.addWidget(self.font_size_selector)

        main_layout.addWidget(self.toolbar)  # Toolbar über den Notizen

        # **🔹 1. Bereich: Allgemeine Notizen**
        self.generalNotesLabel = QLabel("Allgemeine Notizen:")
        self.generalNotes = QTextEdit()
        main_layout.addWidget(self.generalNotesLabel)
        main_layout.addWidget(self.generalNotes)
        self.change_font_size(12)
        # **🔹 2. Bereich: Tabelle & Vorschau nebeneinander**
        bottom_layout = QHBoxLayout()

        # Screenshot-Tabelle (2/3 Breite)
        self.screenshotTable = QTableWidget()
        self.screenshotTable.setColumnCount(2)
        self.screenshotTable.setHorizontalHeaderLabels(["Screenshot", "Bemerkung"])

        # **🔹 Automatische Spaltenverteilung**
        header = self.screenshotTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Screenshot-Name dehnt sich mit
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Bemerkung dehnt sich mit

        self.screenshotTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.screenshotTable.customContextMenuRequested.connect(self.open_context_menu)
        self.screenshotTable.itemSelectionChanged.connect(self.load_screenshot)
        self.screenshotTable.itemChanged.connect(self.save_screenshot_note)
        bottom_layout.addWidget(self.screenshotTable, 2)  # 2/3 der Breite

        # Screenshot-Vorschau (1/3 Breite)
        self.screenshotPreview = QLabel("Screenshot-Vorschau")
        self.screenshotPreview.setAlignment(Qt.AlignCenter)
        self.screenshotPreview.setStyleSheet("border: 1px solid black; min-height: 300px;")
        bottom_layout.addWidget(self.screenshotPreview, 1)  # 1/3 der Breite

        # Beide Layouts in das Hauptlayout einfügen
        main_layout.addLayout(bottom_layout)

        # **🔹 3. Bereich: Buttons für Steuerung**
        button_layout = QHBoxLayout()
        # **Debrief starten (Trainingsdaten auf Server hochladen)**
        self.debriefButton = QPushButton("Debrief starten")
        self.debriefButton.clicked.connect(self.start_debrief)
        button_layout.addWidget(self.debriefButton)

        # **Refresh-Button (Screenshots neu laden)**
        self.refreshButton = QPushButton("🔄 Refresh")
        self.refreshButton.clicked.connect(self.update_screenshot_list)
        button_layout.addWidget(self.refreshButton)

        # **Speichern-Button (Screenshot-Bemerkungen & Notizen speichern)**
        self.saveButton = QPushButton("💾 Speichern")
        self.saveButton.clicked.connect(self.save_all_data)
        button_layout.addWidget(self.saveButton)

        main_layout.addLayout(button_layout)  # Buttons zum Hauptlayout hinzufügen


        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_training_data()

    def load_training_data(self):
        """Lädt vorhandene Screenshots und Notizen. Erstellt Dateien falls sie fehlen."""
        comments_file = os.path.join(self.training_folder, "comments.json")
        notes_file = os.path.join(self.training_folder, "notes.txt")

        # Falls das Trainingsverzeichnis nicht existiert → erstelle es
        if not os.path.exists(self.training_folder):
            os.makedirs(self.training_folder)

        # Falls die Notizen-Datei nicht existiert → erstelle leere Datei
        if not os.path.exists(notes_file):
            with open(notes_file, "w", encoding="utf-8") as f:
                f.write("")
        
        # Falls die Kommentare-Datei nicht existiert → erstelle leeres JSON
        if not os.path.exists(comments_file):
            with open(comments_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

        # Lade allgemeine Notizen
        with open(notes_file, "r", encoding="utf-8") as f:
            self.generalNotes.setText(f.read())

        """Lädt Screenshots & Bemerkungen in die Tabelle."""
        screenshots = self.screenshot_manager.get_screenshots()
        self.screenshotTable.setRowCount(len(screenshots))

        # Lade bestehende Bemerkungen
        comments = self.screenshot_manager.load_all_comments()

        for row, screenshot in enumerate(screenshots):
            filename_item = QTableWidgetItem(screenshot)
            filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)  # Filename nicht editierbar

            # Lade bestehende Bemerkung oder setze leeren Text
            comment_text = comments.get(screenshot, "")
            comment_item = QTableWidgetItem(comment_text)

            self.screenshotTable.setItem(row, 0, filename_item)
            self.screenshotTable.setItem(row, 1, comment_item)

            # Falls kein Kommentar existiert, fokussiere direkt das Feld
            if comment_text == "":
                self.screenshotTable.setCurrentCell(row, 1)

    def update_screenshot_list(self):
        """Aktualisiert die Screenshot-Tabelle."""
        self.screenshotTable.clearContents()
        self.screenshotTable.setRowCount(0)  # Zurücksetzen

        screenshots = self.screenshot_manager.get_screenshots()
        comments = self.screenshot_manager.load_all_comments()

        self.screenshotTable.setRowCount(len(screenshots))

        for row, screenshot in enumerate(screenshots):
            filename_item = QTableWidgetItem(screenshot)
            filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)  # Name nicht editierbar

            comment_text = comments.get(screenshot, "")
            comment_item = QTableWidgetItem(comment_text)

            self.screenshotTable.setItem(row, 0, filename_item)
            self.screenshotTable.setItem(row, 1, comment_item)


    def load_screenshot(self):
        """Lädt den Screenshot in die Vorschau, wenn eine Zeile angeklickt wird."""
        selected_row = self.screenshotTable.currentRow()
        if selected_row == -1:
            return

        screenshot_name = self.screenshotTable.item(selected_row, 0).text()
        screenshot_path = os.path.join(self.screenshot_manager.training_folder,"screenshots", screenshot_name)

        if os.path.exists(screenshot_path):
            self.screenshotPreview.setPixmap(QPixmap(screenshot_path).scaled(400, 300, Qt.KeepAspectRatio))
        else:
            self.screenshotPreview.setText("Fehler: Datei nicht gefunden")


    def on_new_screenshot_detected(self, screenshot_path):
        """
        Wird aufgerufen, wenn ein neuer Screenshot im Screenshot-Ordner erkannt wird.
        Falls das Debrief bereits gestartet wurde, wird der Screenshot automatisch hochgeladen.
        """
        screenshot_name = os.path.basename(screenshot_path)

        if self.screenshot_notes_window:
                self.screenshot_notes_window.update_screenshot(screenshot_name)
                
        if self.server_uploader:
            print(f"📸 Neuer Screenshot erkannt: {screenshot_name} (wird hochgeladen)")
            self.upload_screenshot(screenshot_name, screenshot_path)  # ✅ Hochladen
        else:
            print(f"📸 Neuer Screenshot erkannt: {screenshot_name} (aber Debrief noch nicht gestartet)")




    def upload_screenshot(self, screenshot_name, screenshot_path):
        """Lädt einen Screenshot automatisch auf den Server hoch."""
        if not os.path.exists(screenshot_path):
            QMessageBox.warning(self, "Fehler", f"Screenshot '{screenshot_name}' wurde nicht gefunden.")
            return

        # **Prüfen, ob eine `training_id` existiert**
        if not self.server_uploader.training_id:
            print(f"⚠️ Screenshot '{screenshot_name}' konnte nicht hochgeladen werden (Debrief nicht gestartet).")
            return

        try:
            with open(screenshot_path, "rb") as file:
                encoded_string = base64.b64encode(file.read()).decode("utf-8")

            url = f"{self.server_uploader.api_base_url}/{self.server_uploader.training_id}/upload"
            payload = {
                "file": encoded_string,
                "filename": screenshot_name
            }

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                print(f"✅ Screenshot '{screenshot_name}' erfolgreich hochgeladen.")
            else:
                print(f"⚠️ Fehler beim Hochladen von {screenshot_name}: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Fehler beim Hochladen von {screenshot_name}: {e}")


    def save_general_notes(self):
        """Speichert die allgemeinen Notizen."""
        self.screenshot_manager.save_general_notes(self.generalNotes)

    def save_screenshot_note(self, item):
        """Speichert die Bemerkung zum Screenshot, wenn die zweite Spalte geändert wird."""
        if item.column() == 1:  # Nur Änderungen in der Bemerkungs-Spalte speichern
            screenshot_name = self.screenshotTable.item(item.row(), 0).text()
            comment = item.text()
            self.screenshot_manager.save_screenshot_comment(screenshot_name, comment)

    def save_all_data(self):
        """Speichert allgemeine Notizen & Screenshot-Bemerkungen."""
        self.save_general_notes()

        for row in range(self.screenshotTable.rowCount()):
            screenshot_name = self.screenshotTable.item(row, 0).text()
            comment = self.screenshotTable.item(row, 1).text()
            self.screenshot_manager.save_screenshot_comment(screenshot_name, comment)

        print("✅ Alle Daten gespeichert!")

    def open_context_menu(self, position):
        """Öffnet das Kontextmenü bei Rechtsklick auf einen Screenshot."""
        menu = QMenu()

        open_paint_action = QAction("In Paint öffnen", self)
        open_paint_action.triggered.connect(self.open_in_paint)
        menu.addAction(open_paint_action)

        delete_action = QAction("Screenshot löschen", self)
        delete_action.triggered.connect(self.delete_screenshot)
        menu.addAction(delete_action)

        menu.exec_(self.screenshotTable.viewport().mapToGlobal(position))

    def open_in_paint(self):
        """Ruft die Paint-Funktion aus `screenshot_manager.py` auf."""
        selected_row = self.screenshotTable.currentRow()
        if selected_row != -1:
            screenshot_name = self.screenshotTable.item(selected_row, 0).text()
            self.screenshot_manager.open_in_paint(screenshot_name)

    def delete_screenshot(self):
        """Ruft die Lösch-Funktion aus `screenshot_manager.py` auf."""
        selected_row = self.screenshotTable.currentRow()
        if selected_row != -1:
            screenshot_name = self.screenshotTable.item(selected_row, 0).text()
            self.screenshot_manager.delete_screenshot(screenshot_name)
            self.update_screenshot_list()  # Nach dem Löschen Liste aktualisieren


    def start_debrief(self):
        """Speichert alle Daten & lädt sie auf den Server hoch."""
        self.save_all_data()  # Lokale Speicherung vor dem Upload
        self.server_uploader = server_uploader.ServerUploader(self.trainee_name, self.training_name, self.training_date)  
        self.progress_window = ProgressWindow(self.server_uploader)
        self.progress_window.show()


    def open_trainee_window(self):
        """Öffnet das Trainee-Verwaltungsfenster."""
        from gui.trainee_window import TraineeWindow
        self.trainee_window = TraineeWindow()
        self.trainee_window.show()
   
    def open_akte_window(self):
        """Öffnet die Akte für das aktuelle Training."""
        self.akte_window = AkteWindow(self.training_name, self.training_date, self.training_folder)
        self.akte_window.show()

    def open_notes_window(self):
        """Öffnet das Notizen-Popout-Fenster & verbindet es mit den General Notes."""
        self.notes_window = NotesWindow(self.training_folder)
        self.notes_window.notes_updated.connect(self.update_general_notes)  # ✅ Verbindung zum Signal
        self.notes_window.show()

    def update_general_notes(self, text):
        """Aktualisiert das General Notes Feld im TrainingWindow, wenn sich Notizen ändern."""
        self.generalNotes.setPlainText(text)  # ✅ Automatische Aktualisierung

    
    def end_training(self):
        """Speichert das Training und schließt das Fenster."""
        self.save_all_data()
        self.close()
        self.open_trainee_window()


    def toggle_bold(self):
        """Schaltet den fetten Text um."""
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.generalNotes.fontWeight() != QFont.Bold else QFont.Normal)
        self.generalNotes.mergeCurrentCharFormat(fmt)

    def toggle_italic(self):
        """Schaltet kursiven Text um."""
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.generalNotes.fontItalic())
        self.generalNotes.mergeCurrentCharFormat(fmt)

    def toggle_underline(self):
        """Schaltet unterstrichenen Text um."""
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.generalNotes.fontUnderline())
        self.generalNotes.mergeCurrentCharFormat(fmt)

    def change_font(self, font):
        """Ändert die Schriftart."""
        fmt = QTextCharFormat()
        fmt.setFont(font)
        self.generalNotes.mergeCurrentCharFormat(fmt)

    def change_font_size(self, size):
        """Ändert die Schriftgröße."""
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self.generalNotes.mergeCurrentCharFormat(fmt)

    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird."""
        self.screenshot_manager.stop_watching()
        event.accept()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrainingWindow()
    window.show()
    sys.exit(app.exec_())
