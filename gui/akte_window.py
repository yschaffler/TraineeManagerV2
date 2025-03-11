import datetime
import json
import os
import pyperclip
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit

class AkteWindow(QWidget):
    """Fenster zum Schreiben der Akte während des Trainings."""
    
    def __init__(self, training_name, training_date, training_folder):
        super().__init__()
        self.training_folder = training_folder
        self.akte_file = os.path.join(self.training_folder, "akte.json")

        self.training_name = training_name
        self.training_date = self.format_date(training_date)  # ✅ Datum umformatieren
        self.trainer_initials = ""  # ✅ Trainer-Initialen

        self.initUI()
        self.load_existing_akte()

    def initUI(self):
        """Erstellt die GUI für die Akte."""
        self.setWindowTitle("Akte schreiben")
        self.setGeometry(400, 200, 800, 600)
        layout = QVBoxLayout()

        # **🔹 Editierbare Felder für Trainingsnamen & Trainer-Initialen**
        self.training_name_input = QLineEdit(self.training_name)
        layout.addWidget(QLabel("Training Name:"))
        layout.addWidget(self.training_name_input)

        self.trainer_initials_input = QLineEdit(self.trainer_initials)
        layout.addWidget(QLabel("Trainer Initialen (XY):"))
        layout.addWidget(self.trainer_initials_input)

        # **🔹 Kommentarbereich für Notizen**
        self.comment_text = QTextEdit()
        self.comment_text.setPlaceholderText("Kommentar (ATD only)")
        layout.addWidget(self.comment_text)

        # **🔹 Tabelle für Kriterien, Stärken, Schwächen, Level**
        self.table = QTableWidget(12, 4)
        self.table.setHorizontalHeaderLabels(["Criteria", "Strengths", "Weaknesses", "Level"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        criteria = [
            "Theory", "Phraseology / Radiotelephony", "Coordination", "Tag management / FPL handling",
            "Situational awareness", "Problem recognition", "Traffic planning", "Reaction", "Separation",
            "Efficiency", "Ability to work under pressure", "Manner and motivation"
        ]
        for row, criterion in enumerate(criteria):
            item = QTableWidgetItem(criterion)
            item.setFlags(item.flags() & ~2)  # **Nicht editierbar**
            self.table.setItem(row, 0, item)

        layout.addWidget(self.table)

        # **🔹 Buttons für Speichern & Kopieren**
        self.save_button = QPushButton("Akte speichern")
        self.save_button.clicked.connect(self.save_akte)
        layout.addWidget(self.save_button)

        self.copy_button = QPushButton("Code in Zwischenablage kopieren")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

    def load_existing_akte(self):
        """Lädt eine bestehende Akte aus JSON, falls sie existiert."""
        akte_file = os.path.join(self.training_folder, "akte.json")

        if os.path.exists(akte_file):
            try:
                with open(akte_file, "r", encoding="utf-8") as file:
                    akte_data = json.load(file)

                self.training_name_input.setText(akte_data.get("training_name", ""))
                self.trainer_initials_input.setText(akte_data.get("trainer_initials", ""))
                self.comment_text.setText(akte_data.get("comment", ""))

                for row, entry in enumerate(akte_data["criteria"]):
                    self.table.setItem(row, 1, QTableWidgetItem(entry["strengths"]))
                    self.table.setItem(row, 2, QTableWidgetItem(entry["weaknesses"]))
                    self.table.setItem(row, 3, QTableWidgetItem(entry["level"]))

            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Akte: {e}")

                QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Akte: {e}")

    def populate_fields_from_akte(self, content):
        """Füllt die GUI-Felder mit gespeicherten Daten."""
        lines = content.split("\n")

        try:
            # **🔹 Trainingsname & Initialen aus Header extrahieren**
            header = lines[0].replace("[HEADING=3]", "").replace("[/HEADING]", "").strip()
            header_parts = header.split(" // ")
            if len(header_parts) >= 3:
                self.training_name_input.setText(header_parts[1])
                self.trainer_initials_input.setText(header_parts[2])

            # **🔹 Kommentar suchen & setzen**
            comment_start = next((i for i, line in enumerate(lines) if "[HEADING=3]Comment" in line), None)
            if comment_start is not None:
                self.comment_text.setText("\n".join(lines[comment_start + 1:]))

            # **🔹 Tabelleneinträge füllen**
            for row in range(self.table.rowCount()):
                criterion = self.table.item(row, 0).text()

                # Suche die Zeile, in der das Kriterium beginnt
                criterion_index = next((i for i, line in enumerate(lines) if f"[td]{criterion}[/td]" in line), None)

                if criterion_index is not None:
                    strengths = lines[criterion_index + 1].replace("[td]", "").replace("[/td]", "").strip()
                    weaknesses = lines[criterion_index + 2].replace("[td]", "").replace("[/td]", "").strip()
                    level = lines[criterion_index + 3].replace("[td]", "").replace("[/td]", "").strip()

                    self.table.setItem(row, 1, QTableWidgetItem(strengths if strengths else ""))
                    self.table.setItem(row, 2, QTableWidgetItem(weaknesses if weaknesses else ""))
                    self.table.setItem(row, 3, QTableWidgetItem(level if level else ""))
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Einlesen der Akte: {e}")



    def generate_forum_code(self, akte_data):
        """Wandelt JSON-Daten ins Forum-Format um."""
        self.save_akte()
        heading = f"[HEADING=3]{akte_data['training_date']} // {akte_data['training_name']} // {akte_data['trainer_initials']}[/HEADING]\n\n"

        table = "[TABLE width=\"100%\"]\n"
        table += "[TR][td][B]Criteria[/B][/td][td][B][COLOR=rgb(65, 168, 95)]Strengths[/COLOR][/B][/td][td][B][COLOR=rgb(184, 49, 47)]Weaknesses[/COLOR][/B][/td][td][B]Level[/B][/td][/TR]\n"

        for entry in akte_data["criteria"]:
            table += f"[TR][td]{entry['criterion']}[/td][td]{entry['strengths']}[/td][td]{entry['weaknesses']}[/td][td]{entry['level']}[/td][/TR]\n"

        table += "[/TABLE]\n\n"

        comment_section = f"[HEADING=3]Comment [COLOR=rgb(184, 49, 47)](ATD only)[/COLOR][/HEADING]\n{akte_data['comment']}\n"

        return heading + table + comment_section



    def save_akte(self):
        """Speichert die Akte als JSON-Datei im Trainingsordner."""
        akte_data = {
            "training_name": self.training_name_input.text(),
            "training_date": self.training_date,
            "trainer_initials": self.trainer_initials_input.text(),
            "comment": self.comment_text.toPlainText(),
            "criteria": []
        }

        for row in range(self.table.rowCount()):
            criterion = self.table.item(row, 0).text()
            strengths = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            weaknesses = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            level = self.table.item(row, 3).text() if self.table.item(row, 3) else ""

            akte_data["criteria"].append({
                "criterion": criterion,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "level": level
            })

        akte_file = os.path.join(self.training_folder, "akte.json")

        try:
            with open(akte_file, "w", encoding="utf-8") as file:
                json.dump(akte_data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")



    def copy_to_clipboard(self):
        """Lädt die Akte aus JSON & wandelt sie ins Forum-Format um."""
        akte_file = os.path.join(self.training_folder, "akte.json")

        if not os.path.exists(akte_file):
            QMessageBox.warning(self, "Fehler", "Keine gespeicherte Akte gefunden!")
            return

        try:
            with open(akte_file, "r", encoding="utf-8") as file:
                akte_data = json.load(file)

            forum_code = self.generate_forum_code(akte_data)
            pyperclip.copy(forum_code)
            QMessageBox.information(self, "Erfolg", "Akte wurde in die Zwischenablage kopiert! - Sie kann nun im Forum eingefüht werden")

        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Konvertieren: {e}")


    def format_date(self, date_str):
        """Formatiert das Datum in DDMM(MONAT)YYYY."""
        months = ["JAN", "FEB", "MAR", "APR", "MAI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEC"]
        
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")  # ✅ Standardformat
            formatted_date = dt.strftime(f"%d%b%Y").upper()  # ✅ Format in DDMMMYYYY
            return formatted_date
        except ValueError:
            return date_str  # Falls das Datum fehlerhaft ist, Original zurückgeben
