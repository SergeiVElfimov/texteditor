from src.wordprocessor import MainWindow
from PyQt6.QtWidgets import QApplication
import sys


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName("Free text editor")

    window = MainWindow()
    app.exec()