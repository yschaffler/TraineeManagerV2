import re
import uuid
import requests
import os
import base64
import json
from datetime import datetime

from core.trainee_manager import TraineeManager

class ServerUploader:
    """Hochladen von Trainingsdaten & Screenshots auf den Server."""

    def __init__(self, trainee_name, training_name, training_date, api_base_url="https://yschaffler.de/api/Vatsim/traineemanager/training"):
        self.training_id = str(uuid.uuid4())
        self.api_base_url = api_base_url
        self.training_name = training_name
        self.trainee_name = trainee_name
        self.date = training_date

        print(self.training_id)
        print(self.training_name)
        self.trainee_manager = TraineeManager()
        
        self.training_folder = self.trainee_manager.get_training_folder(trainee_name, training_name)


    def upload_training_data(self):
        """Lädt alle Trainingsdaten auf den Server hoch."""
        url = f"{self.api_base_url}/v2/{self.training_id}/upload"
        print(self.training_folder)
        # Notizen & Screenshot-Bemerkungen sammeln
        notes_file = os.path.join(self.training_folder, "notes.txt")
        general_notes = open(notes_file).read() if os.path.exists(notes_file) else ""

        comments_file = os.path.join(self.training_folder, "comments.json")
        print(comments_file)
        screenshot_comments = json.load(open(comments_file)) if os.path.exists(comments_file) else {}

        trainee_initials = self.get_initials(self.trainee_name)

        data = {
            "training_id": self.training_id,
            "training_name": self.training_name,
            "trainee_name": trainee_initials,
            "date": self.date,
            "general_notes": general_notes,
            "screenshot_comments": screenshot_comments
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("✅ Trainingsdaten erfolgreich hochgeladen!")
            else:
                print(f"⚠️ Fehler beim Hochladen der Trainingsdaten: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Fehler beim Hochladen der Trainingsdaten: {e}")

    def upload_screenshots(self):
        """Lädt Screenshots als Base64-kodierte Daten auf den Server hoch."""
        url = f"{self.api_base_url}/{self.training_id}/upload"
        screenshots_path = os.path.join(self.training_folder, "screenshots")
        print(screenshots_path)

        if not os.path.exists(screenshots_path):
            print("⚠️ Keine Screenshots zum Hochladen gefunden.")
            return

        for screenshot in os.listdir(screenshots_path):
            screenshot_path = os.path.join(screenshots_path, screenshot)
            if not os.path.isfile(screenshot_path):
                continue

            with open(screenshot_path, "rb") as file:
                encoded_string = base64.b64encode(file.read()).decode("utf-8")  # Base64-Kodierung

            payload = {
                "file": encoded_string,
                "filename": screenshot
            }

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                print(f"✅ Screenshot hochgeladen: {screenshot}")
            else:
                print(f"⚠️ Fehler beim Hochladen von {screenshot}: {response.status_code} - {response.text}")

    def get_debrief_links(self):
        """Erzeugt die URLs für Trainer- & Trainee-Debrief-Seiten."""
        base_url = "https://yschaffler.de/vatsim/traineemanager/training"
        trainer_link = f"{base_url}/trainer/{self.training_id}"
        trainee_link = f"{base_url}/trainee/{self.training_id}"
        return trainer_link, trainee_link
    
    def get_initials(self, name):
        """Erzeugt Initialen aus dem Namen, berücksichtigt Großbuchstaben in zusammengesetzten Wörtern."""
        # Entferne alle nicht-alphabetischen Zeichen
        clean_name = re.sub(r'[^A-Za-z]', ' ', name).strip()
        
        # Teile den Namen in Wörter auf
        words = clean_name.split()

        if len(words) >= 2:
            # **Nimm den ersten Buchstaben der ersten zwei Wörter**
            initials = words[0][0] + words[1][0]
        else:
            # **Falls nur ein Wort existiert, prüfe auf Großbuchstaben**
            capital_letters = [char for char in clean_name if char.isupper()]
            if len(capital_letters) >= 2:
                initials = capital_letters[0] + capital_letters[1]  # **Nimm die ersten zwei Großbuchstaben**
            else:
                initials = clean_name[:2].upper()  # **Falls nur kleine Buchstaben, nimm die ersten zwei Buchstaben**

        return initials.upper() if initials else "XX"
    

