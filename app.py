import sys

from PyQt6.QtWidgets import QApplication

from src.wordprocessor import MainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName("Free text editor")

    window = MainWindow()
    app.exec()
