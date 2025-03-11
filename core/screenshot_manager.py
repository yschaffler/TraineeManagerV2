import json
import os
import shutil
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.trainee_manager import TraineeManager


class ScreenshotHandler(FileSystemEventHandler):
    """Watchdog Event-Handler, der neue Screenshots erkennt und verschiebt."""


    def __init__(self, trainee_name, training_name, training_window, gui_callback=None):
        self.screenshot_source = os.path.expanduser("~/Pictures/Screenshots")  # Standard-Screenshot-Ordner
        
        self.trainee_manager = TraineeManager()
        self.training_window = training_window
        self.training_folder = os.path.join(self.trainee_manager.get_training_folder(trainee_name, training_name), "screenshots")
        os.makedirs(self.training_folder, exist_ok=True)
        self.gui_callback = gui_callback 
    
    def on_created(self, event):
        """Wird aufgerufen, wenn eine neue Datei erstellt wird."""
        if event.is_directory:
            return

        file_path = event.src_path
        if file_path.lower().endswith(".png"):
            self.move_screenshot(file_path)

    def move_screenshot(self, file_path):
        """Verschiebt den Screenshot in den aktuellen Trainingsordner."""
        filename = os.path.basename(file_path).replace(" ", "_")
        new_path = os.path.join(self.training_folder, filename)

        time.sleep(0.5)
        try:
            shutil.move(file_path, new_path)
            print(f"✅ Screenshot verschoben: {filename}")
            
            # Falls GUI vorhanden ist, aktualisiere sie
            if self.gui_callback:
                self.gui_callback()

            time.sleep(0.5)
            self.training_window.on_new_screenshot_detected(new_path)

        except Exception as e:
            print(f"⚠️ Fehler beim Verschieben von {filename}: {e}")

class ScreenshotManager:
    """Verwaltet Screenshots & überwacht den Screenshot-Ordner."""

    def __init__(self, trainee_name, training_name, training_window, gui_callback=None):
        self.trainee_manager = TraineeManager()
        self.training_folder = self.trainee_manager.get_training_folder(trainee_name, training_name)
        os.makedirs(self.training_folder, exist_ok=True)
        self.event_handler = ScreenshotHandler(trainee_name, training_name, training_window, gui_callback)
        self.observer = Observer()

    def start_watching(self):
        """Startet die Überwachung des Screenshot-Ordners."""
        self.observer.schedule(self.event_handler, self.event_handler.screenshot_source, recursive=False)
        self.observer.start()
        print(f"📸 Überwachung gestartet: {self.event_handler.screenshot_source}")

    def stop_watching(self):
        """Stoppt die Überwachung."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("🛑 Screenshot-Überwachung gestoppt")

    def open_in_paint(self, screenshot_name):
        """Öffnet den ausgewählten Screenshot in Paint."""
        screenshot_path = os.path.abspath(os.path.join(self.training_folder, "screenshots", screenshot_name))
        print(screenshot_path)
        if os.path.exists(screenshot_path):
            print("exists")
            subprocess.run(["mspaint", screenshot_path], check=False)
        
    def delete_screenshot(self, screenshot_name):
        """Löscht den ausgewählten Screenshot nach Bestätigung."""
        screenshot_path = os.path.abspath(os.path.join(self.training_folder, "screenshots", screenshot_name))
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            print(f"🗑️ Screenshot gelöscht: {screenshot_path}")


    def get_screenshots(self):
        """Gibt eine Liste aller Screenshots im Trainingsordner zurück."""
        screenshots_path = os.path.join(self.training_folder, "screenshots")

        if not os.path.exists(screenshots_path):
            return []

        # Lade nur PNG-Dateien, sortiere sie nach Erstellungszeit
        screenshots = [f for f in os.listdir(screenshots_path) if f.lower().endswith(".png")]
        screenshots.sort(key=lambda x: os.path.getctime(os.path.join(screenshots_path, x)))  # Sortiert nach Erstellungsdatum

        return screenshots
    



    def save_screenshot_comment(self, screenshot_name, comment):
        """Speichert die Bemerkung zu einem Screenshot."""
        comments_file = os.path.join(self.training_folder, "comments.json")

        # Falls Datei nicht existiert, erstelle eine leere JSON-Struktur
        if not os.path.exists(comments_file):
            with open(comments_file, "w") as f:
                json.dump({}, f)

        with open(comments_file, "r+", encoding="utf-8") as f:
            comments = json.load(f)
            comments[screenshot_name.replace(" ", "_")] = comment
            f.seek(0)
            json.dump(comments, f, indent=4)
            f.truncate()
    
    def load_all_comments(self):
        """Lädt alle Bemerkungen aus `comments.json`."""
        comments_file = os.path.join(self.training_folder, "comments.json")

        if not os.path.exists(comments_file):
            return {}

        with open(comments_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_general_notes(self, generalNotes):
        """Speichert die allgemeinen Notizen."""
        notes_file = os.path.join(self.training_folder, "notes.txt")
        with open(notes_file, "w", encoding="utf-8") as f:
            f.write(generalNotes.toPlainText())
