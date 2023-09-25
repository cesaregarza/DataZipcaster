import logging

from PyQt5.QtWidgets import QApplication

from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.ui_manager import UIManager


class App:
    """Main class for the UI. This is the class that is run when the program
    is started.
    """

    def __init__(self) -> None:
        self.app = QApplication([])
        self.base = BaseClass()
        self.ui_manager = UIManager(self.base)

    def run(self) -> None:
        """Runs the UI."""
        logging.info("Starting UI")
        self.base.show()
        self.app.exec_()
        logging.info("UI closed")
