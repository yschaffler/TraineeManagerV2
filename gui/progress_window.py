import sys
import requests
import webbrowser
import pyperclip
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.server_uploader import ServerUploader

class UploadThread(QThread):
    """Hintergrund-Thread für den Upload-Prozess"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)

    def __init__(self, server_uploader):
        super().__init__()
        self.server_uploader = server_uploader

    def run(self):
        """Startet den Upload und sendet Fortschrittssignale"""
        self.server_uploader.upload_training_data()
        self.progress.emit(50)  # 50% Fortschritt nach Trainingsdaten-Upload

        self.server_uploader.upload_screenshots()
        self.progress.emit(100)  # 100% Fortschritt nach Screenshot-Upload

        trainer_link, trainee_link = self.server_uploader.get_debrief_links()
        self.finished.emit(trainer_link, trainee_link)

class ProgressWindow(QWidget):
    """Fenster mit Fortschrittsanzeige für den Upload"""

    def __init__(self, server_uploader):
        super().__init__()
        self.server_uploader = server_uploader

        self.initUI()

        self.upload_thread = UploadThread(server_uploader)
        self.upload_thread.progress.connect(self.update_progress)
        self.upload_thread.finished.connect(self.upload_complete)
        self.upload_thread.start()

    def initUI(self):
        self.setWindowTitle("Upload läuft...")
        self.setGeometry(400, 300, 400, 150)
        layout = QVBoxLayout()

        self.label = QLabel("Trainingsdaten werden hochgeladen...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        layout.addWidget(self.progressBar)

        self.cancelButton = QPushButton("Abbrechen")
        self.cancelButton.clicked.connect(self.cancel_upload)
        layout.addWidget(self.cancelButton)

        self.setLayout(layout)

    def update_progress(self, value):
        """Aktualisiert die Fortschrittsanzeige"""
        self.progressBar.setValue(value)

    def upload_complete(self, trainer_link, trainee_link):
        """Wird aufgerufen, wenn der Upload abgeschlossen ist"""
        self.label.setText("Upload abgeschlossen!")

        webbrowser.open(trainer_link)  # Öffnet die Trainer-Debrief-Seite im Browser
        pyperclip.copy(trainee_link)  # Kopiert den Trainee-Link in die Zwischenablage

        self.show_link_popup()
        self.close()

    def show_link_popup(self):
        """Zeigt eine Nachricht mit den Debrief-Links."""
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Debrief Links")
        msg.setText("Der Link zum Traineedebrief wurde in die Zwischenablage kopiert")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def cancel_upload(self):
        """Schließt das Fenster"""
        self.upload_thread.terminate()
        self.close()
