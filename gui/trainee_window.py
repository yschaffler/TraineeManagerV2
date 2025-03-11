from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QInputDialog, QMenuBar, QAction, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from core.trainee_manager import TraineeManager
from gui.training_window import TrainingWindow

class TraineeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.trainee_manager = TraineeManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Trainee Verwaltung")
        self.setGeometry(300, 300, 600, 500)


        # **🔹 Menüleiste erstellen**
        menubar = self.menuBar()

        # **🔹 Trainings-Menü**
        training_menu = menubar.addMenu("Trainings")
        self.create_training_action = QAction("Erstellen", self)
        self.create_training_action.triggered.connect(self.create_training)
        training_menu.addAction(self.create_training_action)

        open_training_action = QAction("Öffnen", self)
        open_training_action.triggered.connect(self.open_training)
        training_menu.addAction(open_training_action)

        self.rename_training_action = QAction("Umbenennen", self)
        self.rename_training_action.setDisabled(True)  # Standardmäßig deaktiviert
        self.rename_training_action.triggered.connect(self.rename_training)
        training_menu.addAction(self.rename_training_action)

        self.delete_training_action = QAction("Löschen", self)
        self.delete_training_action.setDisabled(True)  # Standardmäßig deaktiviert
        self.delete_training_action.triggered.connect(self.delete_training)
        training_menu.addAction(self.delete_training_action)

        # **🔹 Trainee-Menü**
        trainee_menu = menubar.addMenu("Trainee")

        create_trainee_action = QAction("Erstellen", self)
        create_trainee_action.triggered.connect(self.create_trainee)
        trainee_menu.addAction(create_trainee_action)

        self.rename_trainee_action = QAction("Umbenennen", self)
        self.rename_trainee_action.setDisabled(True)
        self.rename_trainee_action.triggered.connect(self.rename_trainee)
        trainee_menu.addAction(self.rename_trainee_action)

        # **🔹 Einstellungen-Menü**
        settings_menu = menubar.addMenu("Einstellungen")
        select_folder_action = QAction("Trainee-Ordner auswählen", self)
        select_folder_action.triggered.connect(self.select_trainee_folder)
        settings_menu.addAction(select_folder_action)

        main_layout = QVBoxLayout()

        # Suchfeld für Trainees
        search_layout = QHBoxLayout()
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Trainee suchen...")
        self.searchInput.textChanged.connect(self.filter_trainees)
        search_layout.addWidget(self.searchInput)

        main_layout.addLayout(search_layout)

        # **🔹 Trainee-Liste mit Kontextmenü**
        self.traineeList = QListWidget()
        self.traineeList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.traineeList.customContextMenuRequested.connect(self.open_trainee_context_menu)
        self.traineeList.itemClicked.connect(self.load_trainings)
        self.traineeList.itemSelectionChanged.connect(self.update_menu_state)
        main_layout.addWidget(self.traineeList)

        # **🔹 Trainings-Liste mit Kontextmenü**
        self.trainingList = QListWidget()
        self.trainingList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.trainingList.customContextMenuRequested.connect(self.open_training_context_menu)
        self.trainingList.itemSelectionChanged.connect(self.update_menu_state)
        main_layout.addWidget(self.trainingList)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_trainees()

    def load_trainees(self):
        """Lädt die Trainee-Liste."""
        self.traineeList.clear()
        self.traineeList.addItems(self.trainee_manager.get_trainees())

    def filter_trainees(self):
        """Filtert die Trainee-Liste basierend auf der Sucheingabe."""
        search_text = self.searchInput.text().lower()
        self.traineeList.clear()
        for trainee in self.trainee_manager.get_trainees():
            if search_text in trainee.lower():
                self.traineeList.addItem(trainee)

    def create_trainee(self):
        """Erstellt einen neuen Trainee."""
        new_name, ok = QInputDialog.getText(self, "Neuer Trainee", "Namen des neuen Trainees eingeben:")
        
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()

        if new_name in self.trainee_manager.get_trainees():
            QMessageBox.warning(self, "Fehler", f"Der Trainee '{new_name}' existiert bereits.")
            return

        self.trainee_manager.add_trainee(new_name)
        self.load_trainees()

    def rename_trainee(self):
        """Benennt einen Trainee um."""
        selected_trainee = self.traineeList.currentItem()
        if not selected_trainee:
            QMessageBox.warning(self, "Fehler", "Kein Trainee ausgewählt.")
            return

        old_name = selected_trainee.text()
        new_name, ok = QInputDialog.getText(self, "Trainee umbenennen", "Neuen Namen eingeben:", text=old_name)

        if ok and new_name.strip():
            self.trainee_manager.rename_trainee(old_name, new_name.strip())
            self.load_trainees()

    def select_trainee_folder(self):
        """Lässt den Nutzer einen neuen Trainee-Ordner auswählen & lädt die Trainees neu."""
        new_folder = self.trainee_manager.set_trainee_folder()
        if new_folder:
            self.load_trainees()



    def load_trainings(self):
        """Lädt die Trainings des gewählten Trainees."""
        selected_item = self.traineeList.currentItem()
        if not selected_item:
            return
        trainee_name = selected_item.text()
        self.trainingList.clear()
        self.trainingList.addItems(self.trainee_manager.get_trainings(trainee_name))

    def create_training(self):
        """Erstellt ein neues Training."""
        selected_trainee = self.traineeList.currentItem()
        if not selected_trainee:
            QMessageBox.warning(self, "Fehler", "Kein Trainee ausgewählt.")
            return

        trainee_name = selected_trainee.text()
        training_name, ok = QInputDialog.getText(self, "Neues Training", "Namen des neuen Trainings eingeben:")

        if ok and training_name.strip():
            training_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.trainee_manager.add_training(trainee_name, training_name.strip())

            self.training_window = TrainingWindow(trainee_name, training_name.strip(), training_date)
            self.training_window.show()
            self.close()

    def open_training(self):
        """Erstellt ein Training öffnen."""
        selected_trainee = self.traineeList.currentItem()
        if not selected_trainee:
            QMessageBox.warning(self, "Fehler", "Kein Trainee ausgewählt.")
            return

        trainee_name = selected_trainee.text()
        training_name = self.trainingList.currentItem().text()


        training_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.trainee_manager.add_training(trainee_name, training_name.strip())

        self.training_window = TrainingWindow(trainee_name, training_name.strip(), training_date)
        self.training_window.show()
        self.close()

    def rename_training(self):
        """Fragt nach einem neuen Namen und benennt das Training um."""
        selected_trainee = self.traineeList.currentItem()
        selected_training = self.trainingList.currentItem()

        if not selected_trainee or not selected_training:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einen Trainee und ein Training auswählen.")
            return

        old_name = selected_training.text()
        trainee_name = selected_trainee.text()

        # **💡 `QInputDialog.getText()` verwenden, um den neuen Namen abzufragen**
        new_name, ok = QInputDialog.getText(self, "Training umbenennen", "Neuen Namen eingeben:", text=old_name)

        if ok and new_name.strip():
            self.trainee_manager.rename_training(trainee_name, old_name, new_name.strip())
            self.load_trainings()
            QMessageBox.information(self, "Erfolg", f"Training '{old_name}' wurde in '{new_name.strip()}' umbenannt.")


    def delete_training(self):
        """Fragt den Nutzer, bevor ein Training gelöscht wird."""
        selected_trainee = self.traineeList.currentItem()
        selected_training = self.trainingList.currentItem()

        if not selected_trainee or not selected_training:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einen Trainee und ein Training auswählen.")
            return

        trainee_name = selected_trainee.text()
        training_name = selected_training.text()

        reply = QMessageBox.question(self, "Training löschen",
                                    f"Möchtest du das Training '{training_name}' wirklich löschen?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.trainee_manager.delete_training(trainee_name, training_name)
            self.load_trainings()

    def open_trainee_context_menu(self, position):
        """Öffnet das Kontextmenü für Trainees."""
        menu = QMenu()

        create_action = QAction("Trainee erstellen", self)
        create_action.triggered.connect(self.create_trainee)
        menu.addAction(create_action)

        rename_action = QAction("Trainee umbenennen", self)
        rename_action.triggered.connect(self.rename_trainee)
        menu.addAction(rename_action)

        menu.exec_(self.traineeList.viewport().mapToGlobal(position))

    def open_training_context_menu(self, position):
        """Öffnet das Kontextmenü für Trainings."""
        menu = QMenu()

        create_action = QAction("Training erstellen", self)
        create_action.triggered.connect(self.create_training)
        menu.addAction(create_action)

        open_action = QAction("Training öffnen", self)
        open_action.triggered.connect(self.open_training)
        menu.addAction(open_action)

        rename_action = QAction("Training umbenennen", self)
        rename_action.triggered.connect(self.rename_training)
        menu.addAction(rename_action)

        delete_action = QAction("Training löschen", self)
        delete_action.triggered.connect(self.delete_training)
        menu.addAction(delete_action)

        menu.exec_(self.trainingList.viewport().mapToGlobal(position))

    def update_menu_state(self):
        """Aktualisiert die Aktivierung der Menüeinträge basierend auf der Auswahl."""
        trainee_selected = self.traineeList.currentItem() is not None
        training_selected = self.trainingList.currentItem() is not None

        self.rename_trainee_action.setEnabled(trainee_selected)
        self.create_training_action.setEnabled(trainee_selected)
        self.rename_training_action.setEnabled(training_selected)
        self.delete_training_action.setEnabled(training_selected)



