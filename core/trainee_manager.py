import os
import json
from PyQt5.QtWidgets import QFileDialog

class TraineeManager:
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.trainee_folder = self.load_trainee_folder()

    def load_trainee_folder(self):
        """Lädt den gespeicherten Trainee-Ordner oder fragt den Nutzer beim ersten Mal."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("trainee_folder", "")

        return self.set_trainee_folder()

    def set_trainee_folder(self):
        """Lässt den Nutzer einen neuen Trainee-Ordner auswählen & speichert ihn."""
        folder = QFileDialog.getExistingDirectory(None, "Trainee-Ordner auswählen")
        if folder:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"trainee_folder": folder}, f)
            self.trainee_folder = folder
        return folder
    
    def get_training_folder(self, trainee_name, training_name):
        """Gibt den vollen Pfad eines Trainings zurück."""
        if not self.trainee_folder:
            raise ValueError("Kein Trainee-Ordner gesetzt. Bitte zuerst den Trainee-Ordner auswählen.")
        return os.path.join(self.trainee_folder, trainee_name, training_name)

    def get_trainees(self):
        """Gibt eine Liste aller Trainees zurück (Ordner im Trainee-Verzeichnis)."""
        if not self.trainee_folder:
            return []
        return [f for f in os.listdir(self.trainee_folder) if os.path.isdir(os.path.join(self.trainee_folder, f))]

    def add_trainee(self, trainee_name):
        """Erstellt einen neuen Trainee-Ordner."""
        trainee_path = os.path.join(self.trainee_folder, trainee_name)
        
        if os.path.exists(trainee_path):
            print(f"⚠️ Trainee '{trainee_name}' existiert bereits.")
            return

        os.makedirs(trainee_path)
        print(f"✅ Neuer Trainee erstellt: {trainee_name}")


    def get_trainings(self, trainee_name):
        """Gibt alle Trainings eines Trainees zurück (Ordner im Trainee-Ordner)."""
        trainee_path = os.path.join(self.trainee_folder, trainee_name)
        if not os.path.exists(trainee_path):
            return []
        return [f for f in os.listdir(trainee_path) if os.path.isdir(os.path.join(trainee_path, f))]

    def add_training(self, trainee_name, training_name):
        """Erstellt einen neuen Trainingsordner für einen Trainee."""
        training_path = os.path.join(self.trainee_folder, trainee_name, training_name)
        if not os.path.exists(training_path):
            os.makedirs(training_path)
            print(f"✅ Training hinzugefügt: {training_name}")

    def rename_trainee(self, old_name, new_name):
        """Benennt einen Trainee-Ordner um."""
        old_path = os.path.join(self.trainee_folder, old_name)
        new_path = os.path.join(self.trainee_folder, new_name)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"✅ Trainee umbenannt: {old_name} → {new_name}")

    def rename_training(self, trainee_name, old_name, new_name):
        """Benennt ein Training um."""
        old_path = os.path.join(self.trainee_folder, trainee_name, old_name)
        new_path = os.path.join(self.trainee_folder, trainee_name, new_name)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"✅ Training umbenannt: {old_name} → {new_name}")

    def delete_training(self, trainee_name, training_name):
        """Löscht ein Training vollständig."""
        training_path = os.path.join(self.trainee_folder, trainee_name, training_name)
        if os.path.exists(training_path):
            for root, dirs, files in os.walk(training_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(training_path)
            print(f"🗑️ Training gelöscht: {training_name}")
