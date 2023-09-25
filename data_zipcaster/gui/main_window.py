import logging
import os
import pathlib
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QWidget,
)

from data_zipcaster import __version__
from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.constants import GUIStates
from data_zipcaster.gui.exceptions import CancelFetchException
from data_zipcaster.gui.utils import SplatNet_Scraper_Wrapper
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"


class App(BaseClass):
    ready_signal = pyqtSignal(bool)
    fetch_signal = pyqtSignal()
    cancel_signal = pyqtSignal()
    set_scraper_signal = pyqtSignal(SplatNet_Scraper_Wrapper)

    def __init__(self) -> None:
        logging.debug("Initializing App")
        super().__init__()
        ui_path = pathlib.Path(__file__).parent / "ui" / "main.ui"
        logging.debug(f"Loading UI from {ui_path}")
        uic.loadUi(str(ui_path), self)
        self.cwd = os.getcwd()
        self.scraper: SplatNet_Scraper_Wrapper | None = None
        self.state: GUIStates = GUIStates.INIT
        self.setup_ui()
        self.state: GUIStates = GUIStates.READY
        logging.debug("App initialized")

    def setup_ui(self) -> None:
        self.setup_signals()
        self.hide_progress_bars()
        self.check_config_path_on_init()

        # Disable Salmon Run for now with a tooltip
        self.salmon_check.setEnabled(False)
        self.salmon_check.setToolTip("Salmon Run is not supported yet")

    def setup_signals(self) -> None:
        """Connect signals to slots."""
        logging.debug("Connecting signals")
        self.ready_signal.connect(self.ready_changed)
        self.fetch_signal.connect(self.fetch_started)
        self.cancel_signal.connect(self.cancel_fetch_signal)
        self.set_scraper_signal.connect(self.set_scraper)

    def check_config_path_on_init(self) -> None:
        """Check if a config file exists in the current working directory.

        If a config file exists, enable the "Test Tokens" button.
        """
        logging.debug("Checking for config file")
        config_path = pathlib.Path(self.cwd) / "config.ini"
        if config_path.exists():
            logging.debug("Config file found")
            self.config_path_text.setText(str(config_path))
            self.load_config()

    def load_config(self) -> None:
        """Load a config file."""
        logging.info("Attempting to load config file")
        config_path = self.config_path_text.text()
        self.ready_signal.emit(False)
        if not config_path:
            logging.error("No config file selected")
            self.show_error("Please select a config file first.")
            return
        try:
            logging.debug("Loading config file")
            scraper = SplatNet_Scraper_Wrapper.from_config(config_path)
        except KeyError:
            logging.error("Config file is invalid")
            self.show_error(
                "The config file is invalid. Please make sure the file is "
                "correctly formatted."
            )
            return
        self.set_scraper_signal.emit(scraper)
        logging.debug("Config file loaded")

    def open_file_dialog(self) -> None:
        """Open a file dialog to select a config file."""
        logging.debug("Opening file dialog")
        config_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select config file",
            self.cwd,
            "Config files (*.ini)",
        )
        if config_path:
            logging.debug("Config file selected")
            self.config_path_text.setText(config_path)
            self.cwd = os.path.dirname(config_path)
            self.test_tokens_button_wrapper.set_enabled(True)
            self.load_config_button_wrapper.set_enabled(True)
        else:
            logging.debug("No config file selected")

    def test_tokens(self) -> None:
        """Test the tokens in the config file."""
        logging.info("Testing tokens")
        if self.scraper is None:
            logging.error("No scraper found")
            return

        self.thread = QThread()
        logging.debug("Moving scraper to thread and connecting signals")
        self.scraper.moveToThread(self.thread)
        self.thread.started.connect(self.scraper.test_tokens)
        self.scraper.testing_finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        logging.debug("Starting thread")
        self.thread.start()

    def show_info(self, msg: str, window_title: str = "Info") -> None:
        """Show an info message.

        Args:
            msg (str): The message to show.
            window_title (str): The title of the window. Defaults to "Info".
        """
        logging.debug("Showing info message")
        if self.state == GUIStates.INIT:
            logging.debug("App not started yet, returning")
            return
        info = QMessageBox()
        info.setIcon(QMessageBox.Information)
        info.setText("Info")
        info.setInformativeText(msg)
        info.setWindowTitle(window_title)
        info.setWindowIcon(self.windowIcon())
        info.exec_()

    def show_error(self, msg: str, window_title: str = "Error") -> None:
        """Show an error message.

        Args:
            msg (str): The message to show.
            window_title (str): The title of the window. Defaults to "Error".
        """
        logging.debug("Showing error message")
        if self.state == GUIStates.INIT:
            logging.debug("App not started yet, returning")
            return
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Error")
        error.setInformativeText(msg)
        error.setWindowTitle(window_title)
        error.setWindowIcon(self.windowIcon())
        error.exec_()

    def checkboxes_changed(self) -> None:
        """Check if at least one checkbox is checked."""
        logging.debug("Checking if at least one checkbox is checked")

        if (
            any(checkbox.isChecked() for checkbox in self.checkboxes)
            and self.ready
        ):
            logging.debug(
                "At least one checkbox is checked and tokens are valid"
            )
            self.fetch_button_wrapper.set_enabled(True)
        else:
            logging.debug("No checkboxes are checked or tokens are invalid")
            self.fetch_button_wrapper.set_enabled(False)

    def connect_scraper_signals(self) -> None:
        """Connect signals to slots."""
        logging.debug("Connecting scraper signals")
        self.scraper.testing_started.connect(self.testing_started)
        self.scraper.testing_finished.connect(self.testing_finished)
        self.scraper.progress_outer_changed.connect(self.outer_progress_changed)
        self.scraper.progress_inner_changed.connect(self.inner_progress_changed)

    def fetch_data(self) -> None:
        """Fetch data."""
        logging.info("Fetching data")
        if self.scraper is None:
            logging.error("No scraper found, this should not happen")
            return

        if self.state in (GUIStates.FETCHING, GUIStates.CANCELLING):
            logging.debug("Fetch already in progress, returning")
            return

        self.thread = QThread()
        logging.debug("Moving scraper to thread and connecting signals")
        self.scraper.moveToThread(self.thread)
        partial_fetch_data = partial(
            self.scraper.fetch_data,
            anarchy=self.anarchy_check.isChecked(),
            private=self.private_check.isChecked(),
            turf_war=self.turf_check.isChecked(),
            salmon_run=self.salmon_check.isChecked(),
            x_battle=self.x_check.isChecked(),
            challenge=self.challenge_check.isChecked(),
            limit=self.limit_spinbox.value(),
        )
        self.thread.started.connect(partial_fetch_data)
        self.scraper.fetching_finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        logging.debug("Starting thread")
        self.fetch_signal.emit()
        self.state = GUIStates.FETCHING
        self.thread.start()

    def cancel_fetch(self) -> None:
        """Cancel fetching data."""
        logging.info("Canceling fetch")
        if self.scraper is None:
            logging.error("No scraper found, this should not happen")
            return

        if self.state != GUIStates.FETCHING:
            logging.debug("No fetch in progress, returning")
            return

        self.scraper.cancelled = True
        self.state = GUIStates.CANCELLING
        self.cancel_signal.emit()

    def show_progress_bars(self) -> None:
        """Show the progress bars."""
        logging.debug("Showing progress bars")
        self.widget_outer.hide()
        self.widget_inner.hide()
        self.progress_outer.setValue(0)
        self.progress_inner.setValue(0)
        self.progress_outer.show()
        self.progress_inner.show()

    def hide_progress_bars(self) -> None:
        """Hide the progress bars."""
        logging.debug("Hiding progress bars")
        self.progress_outer.hide()
        self.progress_inner.hide()
        self.widget_outer.show()
        self.widget_inner.show()

    @pyqtSlot()
    def testing_started(self) -> None:
        """Disable the "Test Tokens" button and change its text to "Testing..." """
        logging.debug("Signal received: testing_started")
        self.test_tokens_button_wrapper.set_enabled(False)
        self.test_tokens_button_wrapper.button.setText("Testing...")

    @pyqtSlot(bool)
    def testing_finished(self, success: bool) -> None:
        """Enable the "Test Tokens" button and change its text to "Test Tokens" """
        logging.debug("Signal received: testing_finished")
        self.test_tokens_button_wrapper.set_enabled(True)
        self.test_tokens_button_wrapper.button.setText("Test Tokens")
        self.ready_signal.emit(success)
        if success:
            path = pathlib.Path(self.config_path_text.text())
            if path.exists():
                self.scraper.save_config(str(path))
        else:
            self.show_error("Tokens are invalid!")

    @pyqtSlot(bool)
    def ready_changed(self, ready: bool) -> None:
        """Enable or disable the "Fetch Data" button based on whether the
        scraper is ready.
        """
        logging.debug("Signal received: ready_changed")
        self.ready = ready
        if ready:
            self.status_icon_label.setText("Ready")
            self.status_icon_label.setStyleSheet("color : green;")
        else:
            self.status_icon_label.setText("Not Ready")
            self.status_icon_label.setStyleSheet("color : red;")

    @pyqtSlot()
    def fetch_started(self) -> None:
        """Change the text of the "Fetch Data" button to "Cancel", and turn the
        self.progress_outer and self.progress_inner widgets into progress bars.
        """
        logging.debug("Signal received: fetch_started")
        self.fetch_button_wrapper.button.setText("Cancel")
        self.fetch_button_wrapper.button.clicked.disconnect(self.fetch_data)
        self.fetch_button_wrapper.button.clicked.connect(self.cancel_fetch)
        self.show_progress_bars()

    @pyqtSlot(int, int)
    def outer_progress_changed(
        self, current_value: int, max_value: int
    ) -> None:
        """Set the value of the outer progress bar."""
        logging.debug("Signal received: progress_bar_outer")
        self.progress_outer.setMaximum(max_value)
        self.progress_outer.setValue(current_value)

    @pyqtSlot(int, int)
    def inner_progress_changed(
        self, current_value: int, max_value: int
    ) -> None:
        """Set the value of the inner progress bar."""
        logging.debug("Signal received: progress_bar_inner")
        self.progress_inner.setMaximum(max_value)
        self.progress_inner.setValue(current_value)

    @pyqtSlot()
    def cancel_fetch_signal(
        self,
    ) -> None:
        """Set to the cancelling state."""
        logging.debug("Signal received: cancel_fetch")
        self.fetch_button_wrapper.button.setText("Cancelling...")
        self.fetch_button_wrapper.button.clicked.disconnect(self.cancel_fetch)
        self.fetch_button_wrapper.button.clicked.connect(self.fetch_data)
        self.hide_progress_bars()
        self.fetch_button_wrapper.button.setEnabled(False)
        QTimer.singleShot(3000, self.enable_fetch_button)

    @pyqtSlot()
    def enable_fetch_button(self) -> None:
        """Enable the "Fetch Data" button."""
        logging.debug("Enabling fetch button")
        self.fetch_button_wrapper.button.setText("Fetch Data")
        self.fetch_button_wrapper.button.setEnabled(True)

    @pyqtSlot(SplatNet_Scraper_Wrapper)
    def set_scraper(self, scraper: SplatNet_Scraper_Wrapper) -> None:
        """Set the scraper and make changes that depend on it.

        Args:
            scraper (SplatNet_Scraper_Wrapper): The scraper to set.
        """
        logging.debug("Setting scraper")
        self.scraper = scraper
        self.test_tokens_button_wrapper.set_enabled(True)
        self.load_config_button_wrapper.set_enabled(True)
        self.connect_scraper_signals()
        logging.debug("Scraper set")


if __name__ == "__main__":
    # Reset logging
    logging.root.handlers = []
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication([])
    ex = App()
    ex.show()
    app.exec_()
