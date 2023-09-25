import logging
import pathlib

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMessageBox

from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.constants import GUIStates
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

    def setup_signals(self) -> None:
        base = self.base
        base.ready_signal.connect(self.ready_changed)
        base.state_changed_signal.connect(self.state_changed)
        base.set_scraper_signal.connect(self.set_scraper)

    @pyqtSlot()
    def testing_started(self) -> None:
        """Disable the "Test Tokens" button and change its text to "Testing..." """
        logging.debug("Signal received: testing_started")
        base = self.base
        base.test_tokens_button_wrapper.set_enabled(False)
        base.test_tokens_button.setText("Testing...")

    @pyqtSlot(bool)
    def testing_finished(self, success: bool) -> None:
        """Enable the "Test Tokens" button and change its text to "Test Tokens" """
        logging.debug("Signal received: testing_finished")
        base = self.base
        base.test_tokens_button_wrapper.set_enabled(True)
        base.test_tokens_button.setText("Test Tokens")
        base.ready_signal.emit(success)
        if success:
            path = pathlib.Path(base.config_path_text.text())
            if path.exists():
                base.scraper.save_config(str(path))
        else:
            base.show_error("Tokens are invalid!")

    @pyqtSlot(bool)
    def ready_changed(self, ready: bool) -> None:
        """Enable or disable the "Fetch Data" button based on whether the
        scraper is ready.
        """
        logging.debug("Signal received: ready_changed")
        base = self.base
        base.ready = ready
        if ready:
            base.status_icon_label.setText("Ready")
            base.status_icon_label.setStyleSheet("color : green;")
        else:
            base.status_icon_label.setText("Not Ready")
            base.status_icon_label.setStyleSheet("color : red;")

    @pyqtSlot(GUIStates)
    def state_changed(self, new_state: GUIStates) -> None:
        logging.debug("Signal received: state_changed")
        func_map = {
            GUIStates.NOT_READY: self.state_not_ready,
            GUIStates.READY: self.state_ready,
            GUIStates.TESTING: self.state_testing,
            GUIStates.FETCHING: self.state_fetching,
            GUIStates.CANCELLING: self.state_cancelling,
        }
        func_map[new_state]()

    def state_not_ready(self) -> None:
        logging.info("State changed to NOT_READY")
        base = self.base
        base.ready = False
        base.status_icon_label.setText("Not Ready")
        base.status_icon_label.setStyleSheet("color : red;")
        base.fetch_button_wrapper.set_enabled(False)
        base.view_button_wrapper.set_enabled(False)
        base.export_all_button_wrapper.set_enabled(False)
        base.test_tokens_button_wrapper.set_enabled(True)
        base.test_tokens_button.setText("Test Tokens")

    def state_ready(self) -> None:
        logging.info("State changed to READY")
        base = self.base
        base.ready = True
        base.status_icon_label.setText("Ready")
        base.status_icon_label.setStyleSheet("color : green;")
        base.fetch_button_wrapper.set_enabled(True)
        base.view_button_wrapper.set_enabled(False)
        base.export_all_button_wrapper.set_enabled(False)
        base.test_tokens_button_wrapper.set_enabled(True)
        base.test_tokens_button.setText("Test Tokens")

    def state_testing(self) -> None:
        logging.info("State changed to TESTING")
        base = self.base
        base.test_tokens_button_wrapper.set_enabled(False)
        base.test_tokens_button.setText("Testing...")

    def state_fetching(self) -> None:
        logging.info("State changed to FETCHING")
        base = self.base
        base.fetch_button.setText("Cancel")
        base.fetch_button.clicked.disconnect(self.fetch_data)
        base.fetch_button.clicked.connect(self.cancel_fetch)
        self.ui_manager.show_progress_bars()

    def state_cancelling(self) -> None:
        logging.info("State changed to CANCELLING")
        base = self.base
        base.fetch_button.setText("Cancelling...")
        base.fetch_button.clicked.disconnect(self.cancel_fetch)
        base.fetch_button.clicked.connect(self.fetch_data)
        base.fetch_button.setEnabled(False)
