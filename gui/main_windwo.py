from PyQt5.QtWidgets import QPushButton, QVBoxLayout

from gui.training_window import TrainingWindow
from gui.trainee_window import TraineeWindow


class MainWindow:
    def __init__(self):
        pass

    def initUI(self):
        self.setWindowTitle(f"Trainee Manager {self.training_id}")
        self.setGeometry(200, 200, 900, 600)

       # **🔹 Hauptlayout (vertikal) → Oben Notizen, unten Screenshots**
        main_layout = QVBoxLayout()

        

        # **Refresh-Button (Screenshots neu laden)**
        self.refreshButton = QPushButton("Testtraining")
        self.refreshButton.clicked.connect(self.open_training_window)
        main_layout.addWidget(self.refreshButton)

        # **Speichern-Button (Screenshot-Bemerkungen & Notizen speichern)**
        self.saveButton = QPushButton("Traineemanager")
        self.saveButton.clicked.connect(self.open_trainee_window)
        main_layout.addWidget(self.saveButton)
    
    def open_trainee_window(self):
        """Öffnet das Trainee-Verwaltungsfenster."""
        self.trainee_window = TraineeWindow()
        self.trainee_window.show()

    def open_training_window(self):
        """Öffnet das Trainings-Fenster."""
        self.trainee_window = TrainingWindow()
        self.trainee_window.show()