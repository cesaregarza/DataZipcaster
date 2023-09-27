import logging
import pathlib

from PyQt5.QtCore import QObject, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMessageBox

from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.constants import GUIStates
from data_zipcaster.gui.ui_manager import UIManager
from data_zipcaster.gui.utils import SplatNet_Scraper_Wrapper


class App(QObject):
    """Main class for the UI. This is the class that is run when the program
    is started.
    """

    def __init__(self) -> None:
        super().__init__()
        self.app = QApplication([])
        self.base = BaseClass()
        self.ui_manager = UIManager(self.base)

    def setup(self) -> None:
        """Sets up the UI."""
        logging.info("Finalizing UI setup")
        self.base.show()
        self.setup_signals()
        self.setup_checkboxes()
        self.setup_config_on_init()

    def run(self) -> None:
        """Runs the UI."""
        logging.info("Starting UI")
        self.setup()
        self.app.exec()
        logging.info("UI closed")

    def setup_signals(self) -> None:
        logging.info("Setting up signals")
        base = self.base

        # Base Signals
        base.state_changed_signal.connect(self.state_changed)
        base.set_scraper_signal.connect(self.set_scraper)

        # Button signals
        base.config_path_button.clicked.connect(self.config_button_clicked)
        base.load_config_button.clicked.connect(self.load_config_button_clicked)
        base.test_tokens_button.clicked.connect(self.test_tokens_button_clicked)
        base.fetch_button.clicked.connect(self.fetch_button_clicked)

    def setup_checkboxes(self) -> None:
        logging.info("Setting up checkboxes")
        base = self.base
        for checkbox in base.checkboxes:
            checkbox.stateChanged.connect(self.checkbox_state_changed)

    def setup_config_on_init(self) -> None:
        logging.info("Setting up config on init, if possible")
        base = self.base
        config_path = pathlib.Path(base.cwd) / "config.ini"
        if config_path.exists():
            logging.debug("Config file found, loading it")
            base.config_path_text.setText(str(config_path))
            self.ui_manager.load_config()

    def setup_scraper_signals(self) -> None:
        logging.info("Setting up scraper signals")
        scraper = self.base.scraper
        ui = self.ui_manager
        scraper.testing_finished.connect(self.testing_finished)
        # scraper.fetching_started.connect(self.fetching_started)
        # scraper.fetching_finished.connect(self.fetching_finished)
        scraper.progress_inner_changed.connect(ui.inner_progress_changed)
        scraper.progress_outer_changed.connect(ui.outer_progress_changed)

    @pyqtSlot(bool)
    def testing_finished(self, success: bool) -> None:
        """Enable the "Test Tokens" button and change its text to "Test Tokens" """
        logging.debug("Signal received: testing_finished")
        base = self.base
        if success:
            base.state_changed_signal.emit(GUIStates.READY)
            self.checkbox_state_changed()
            path = pathlib.Path(base.config_path_text.text())
            if path.exists():
                base.scraper.save_config(str(path))
        else:
            base.state_changed_signal.emit(GUIStates.NOT_READY)
            base.show_error("Tokens are invalid!")
    
    @pyqtSlot()
    def fetching_started(self) -> None:
        """Change the state to FETCHING"""
        logging.debug("Signal received: fetching_started")
        base = self.base
        base.state_changed_signal.emit(GUIStates.FETCHING)

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
        self.base.state = new_state
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

    @pyqtSlot(SplatNet_Scraper_Wrapper)
    def set_scraper(self, scraper: SplatNet_Scraper_Wrapper) -> None:
        logging.info("Setting scraper")
        base = self.base
        base.scraper = scraper
        base.state_changed_signal.emit(GUIStates.NOT_READY)
        self.setup_scraper_signals()

    def cancel_fetch(self) -> None:
        logging.info("Cancelling fetch")
        base = self.base
        base.cancel_signal.emit()

    def fetch_data(self) -> None:
        logging.info("Fetching data")
        # TODO: Remove this, it is outdated and superceded by state_changed
        # Instead, this will handle the actual fetching
        base = self.base
        base.fetch_button_wrapper.set_enabled(False)
        base.view_button_wrapper.set_enabled(False)
        base.export_all_button_wrapper.set_enabled(False)
        base.cancel_signal.emit()
        base.fetching_started.emit()

    # Button functions
    def config_button_clicked(self) -> None:
        logging.info("Config path button clicked")
        self.ui_manager.open_file_dialog()

    def load_config_button_clicked(self) -> None:
        logging.info("Load config button clicked")
        self.ui_manager.load_config()

    def test_tokens_button_clicked(self) -> None:
        logging.info("Test tokens button clicked")
        base = self.base
        if base.scraper is None:
            logging.error("No scraper set")
            return

        base.thread = QThread()
        logging.debug("Moving scraper to thread and connecting signals")
        base.scraper.moveToThread(base.thread)
        base.thread.started.connect(base.scraper.test_tokens)
        base.scraper.testing_finished.connect(base.thread.quit)
        base.thread.finished.connect(base.thread.deleteLater)
        logging.debug("Starting thread")
        base.state_changed_signal.emit(GUIStates.NOT_READY)
        base.state_changed_signal.emit(GUIStates.TESTING)
        base.thread.start()

    def fetch_button_clicked(self) -> None:
        logging.info("Fetch button clicked")
        base = self.base
        if base.scraper is None:
            logging.error("No scraper set")
            return
        
        if base.state == GUIStates.FETCHING:
            logging.debug("State is FETCHING, cancelling fetch")
            self.cancel_fetch()
        elif base.state == GUIStates.READY:
            logging.debug("State is READY, fetching data")
            self.fetch_data()
        else:
            logging.error("State is not READY or FETCHING")
            # Do nothing
            return

    def checkbox_state_changed(self) -> None:
        logging.info("Checkbox state changed")
        base = self.base

        if (
            any(checkbox.isChecked() for checkbox in base.checkboxes)
            and base.ready
        ):
            logging.debug(
                "At least one checkbox is checked and scraper is ready"
            )
            base.fetch_button_wrapper.set_enabled(True)
        else:
            logging.debug("No checkboxes are checked or scraper is not ready")
            base.fetch_button_wrapper.set_enabled(False)


if __name__ == "__main__":
    logging.root.handlers = []
    logging.basicConfig(level=logging.DEBUG)
    app = App()
    app.run()
