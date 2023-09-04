from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtCore import pyqtSlot

class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'PyQt5 Simple Example'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 400, 300)

        # Button
        button = QPushButton('Click Me', self)
        button.move(50, 50)
        button.clicked.connect(self.on_click)

        # Label
        self.label = QLabel('Initial Text', self)
        self.label.move(50, 100)

        self.show()

    @pyqtSlot()
    def on_click(self):
        self.label.setText('Button Clicked')

if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec_()
