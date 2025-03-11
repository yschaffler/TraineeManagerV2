import sys
from PyQt5.QtWidgets import QApplication

from gui.trainee_window import TraineeWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TraineeWindow()
    window.show()
    sys.exit(app.exec_())
