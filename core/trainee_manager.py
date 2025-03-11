import os
import json
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication

class TraineeManager:
    CONFIG_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "TraineeManager")  # ✅ Speichert die Datei im Benutzerverzeichnis
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    def __init__(self):
        if not os.path.exists(self.CONFIG_DIR):  # ✅ Falls Verzeichnis nicht existiert, erstellen
            os.makedirs(self.CONFIG_DIR, exist_ok=True)
        self.trainee_folder = self.load_trainee_folder()

    def load_trainee_folder(self):
        """Lädt den gespeicherten Trainee-Ordner aus `config.json`. Falls er fehlt oder ungültig ist, fragt das Programm nach einem neuen."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                if not content:
                    return self.ask_for_trainee_folder()

                config = json.loads(content)

                if "trainee_folder" not in config or not os.path.exists(config["trainee_folder"]):
                    return self.ask_for_trainee_folder()

                return config["trainee_folder"]

            except (json.JSONDecodeError, FileNotFoundError):
                return self.ask_for_trainee_folder()

        return self.ask_for_trainee_folder()

    def ask_for_trainee_folder(self):
        """Öffnet einen Dialog, um den Trainee-Ordner auszuwählen, falls `config.json` fehlt oder ungültig ist."""
        print("🔍 Wähle einen neuen Trainee-Ordner aus.")

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        folder = QFileDialog.getExistingDirectory(None, "Trainee-Ordner auswählen")

        if folder:
            self.save_trainee_folder(folder)
            return folder
        else:
            QMessageBox.critical(None, "Fehler", "Kein Trainee-Ordner gewählt. Das Programm wird beendet.")
            sys.exit(1)

    def save_trainee_folder(self, folder):
        """Speichert den gewählten Trainee-Ordner in `config.json`."""
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"trainee_folder": folder}, f, indent=4, ensure_ascii=False)

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
        """Gibt eine Liste aller Trainee-Ordner zurück. Falls der Pfad ungültig ist, wird der Nutzer aufgefordert, einen neuen zu wählen."""
        if not os.path.exists(self.trainee_folder):
            print(f"❌ Fehler: Der Trainee-Ordner '{self.trainee_folder}' wurde nicht gefunden.")
            self.trainee_folder = self.ask_for_trainee_folder()

        if not self.trainee_folder:
            print("❌ Kein Trainee-Ordner gesetzt. Programm wird beendet.")
            sys.exit(1)

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
