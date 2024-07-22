from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
import time

class WorkerThread(QThread):
    finished = pyqtSignal()

    def run(self):
        while True:
            print("Thread is running...")
            time.sleep(1)
            # Simulate some task
            # Replace this with your actual task logic

            # Check if we need to stop
            if self.isInterruptionRequested():
                break
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')

        layout = QVBoxLayout()

        self.startButton = QPushButton('Start Thread')
        self.startButton.clicked.connect(self.startThread)
        layout.addWidget(self.startButton)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def startThread(self):
        self.workerThread = WorkerThread()
        self.workerThread.finished.connect(self.onThreadFinished)
        self.workerThread.start()

    def closeEvent(self, event):
        # Override closeEvent to handle window closing
        if self.workerThread.isRunning():
            self.workerThread.requestInterruption()
            self.workerThread.finished.connect(self.close)
            event.ignore()
        else:
            event.accept()

    def onThreadFinished(self):
        self.workerThread.deleteLater()
        print("Thread stopped.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())