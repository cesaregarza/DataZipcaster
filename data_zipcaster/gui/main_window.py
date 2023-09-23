import asyncio
import logging
import os
import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
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
from data_zipcaster.gui.exceptions import CancelFetchException
from data_zipcaster.gui.utils import AsyncRunner, SplatNet_Scraper_Wrapper
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"


class App(QMainWindow):
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
        self.ready: bool = False
        self.started: bool = False
        self.async_runner: AsyncRunner | None = None
        self.setup_ui()
        self.started = True
        logging.debug("App initialized")

    def setup_ui(self) -> None:
        """Set up the UI."""
        logging.debug("Setting up UI")
        self.setWindowTitle("Data Zipcaster")
        self.set_icon()
        self.version_label.setText(f"v.{__version__}")

        self.setup_buttons()
        self.setup_sliders_spinboxes()
        self.setup_checkboxes()
        self.setup_signals()
        self.check_config_path_on_init()

        # Disable Salmon Run for now with a tooltip
        self.salmon_check.setEnabled(False)
        self.salmon_check.setToolTip("Salmon Run is not supported yet")

    def setup_buttons(self) -> None:
        """Set up the buttons. Disable buttons initially if necessary."""
        logging.debug("Setting up buttons")
        # Wrap buttons in Button class
        self.fetch_button_wrapper = Button(
            self.fetch_button,
            enabled_tooltip="Fetch data",
            disabled_tooltip="Please select at least one data source first",
            enabled=False,
        )
        self.view_button_wrapper = Button(
            self.view_button,
            enabled_tooltip="View data",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        self.export_all_button_wrapper = Button(
            self.export_all_button,
            enabled_tooltip="Export all data",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        self.config_path_button_wrapper = Button(
            self.config_path_button,
            enabled_tooltip="Select config file",
        )
        self.new_session_button_wrapper = Button(
            self.new_session_button,
            enabled_tooltip="Fetch a new session token",
        )
        self.test_tokens_button_wrapper = Button(
            self.test_tokens_button,
            enabled_tooltip="Test tokens",
            disabled_tooltip="Please load a config file first",
            enabled=False,
        )
        self.load_config_button_wrapper = Button(
            self.load_config_button,
            enabled_tooltip="Load config file",
            disabled_tooltip="Please select a config file first",
            enabled=False,
        )

        # Connect buttons to functions
        self.config_path_button.clicked.connect(self.open_file_dialog)
        self.load_config_button.clicked.connect(self.load_config)
        self.test_tokens_button.clicked.connect(self.test_tokens)
        self.fetch_button.clicked.connect(self.fetch_data)

    def setup_sliders_spinboxes(self) -> None:
        """Set up the sliders and spinboxes."""
        logging.debug("Setting up sliders and spinboxes")
        self.limit_slider_spinbox = SliderSpinbox(
            self.limit_slider,
            self.limit_spinbox,
            enabled=True,
            enabled_tooltip="Limit the number of matches to fetch",
        )
        self.interval_slider_spinbox = SliderSpinbox(
            self.interval_slider,
            self.interval_spinbox,
            enabled=False,
            enabled_tooltip="Set the time interval to fetch data for",
            disabled_tooltip=(
                '"Fetch Continuously" must be checked for this to be enabled'
            ),
        )
        # Link interval to continuous check
        self.interval_slider_spinbox.link_checkbox(self.continuous_check)

    def setup_signals(self) -> None:
        """Connect signals to slots."""
        logging.debug("Connecting signals")
        self.ready_signal.connect(self.ready_changed)
        self.fetch_signal.connect(self.fetch_started)
        self.cancel_signal.connect(self.cancel_fetch_signal)

    @property
    def checkboxes(self) -> list[QCheckBox]:
        return [
            self.anarchy_check,
            self.private_check,
            self.turf_check,
            self.salmon_check,
            self.x_check,
            self.challenge_check,
        ]

    def setup_checkboxes(self) -> None:
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.checkboxes_changed)

    def set_icon(self) -> None:
        """Set the window icon."""
        logging.debug("Setting window icon")
        logo_path = ASSETS_PATH / "dz_logo.png"
        icon = QIcon(str(logo_path))
        self.setWindowIcon(icon)

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
        asyncio.ensure_future(self.scraper.test_tokens())

    def show_info(self, msg: str, window_title: str = "Info") -> None:
        """Show an info message.

        Args:
            msg (str): The message to show.
            window_title (str): The title of the window. Defaults to "Info".
        """
        logging.debug("Showing info message")
        if not self.started:
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
        if not self.started:
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
        try:
            self.fetch_signal.emit()
            self.scraper.fetch_data(
                anarchy=self.anarchy_check.isChecked(),
                private=self.private_check.isChecked(),
                turf_war=self.turf_check.isChecked(),
                salmon_run=self.salmon_check.isChecked(),
                x_battle=self.x_check.isChecked(),
                challenge=self.challenge_check.isChecked(),
                limit=self.limit_spinbox.value(),
            )
        except CancelFetchException:
            logging.info("Fetch canceled")
            return

    def cancel_fetch(self) -> None:
        """Cancel fetching data."""
        logging.info("Canceling fetch")
        if self.scraper is None:
            logging.error("No scraper found, this should not happen")
            return
        self.scraper.cancelled = True
        self.cancel_signal.emit()

    @pyqtSlot()
    def testing_started(self) -> None:
        """Disable the "Test Tokens" button and change its text to "Testing..." """
        logging.debug("Signal received: testing_started")
        self.test_tokens_button_wrapper.set_enabled(False)
        self.test_tokens_button_wrapper.button.setText("Testing...")
        QApplication.processEvents()

    @pyqtSlot(bool)
    def testing_finished(self, success: bool) -> None:
        """Enable the "Test Tokens" button and change its text to "Test Tokens" """
        logging.debug("Signal received: testing_finished")
        self.test_tokens_button_wrapper.set_enabled(True)
        self.test_tokens_button_wrapper.button.setText("Test Tokens")
        QApplication.processEvents()
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
            self.status_icon.setText("Ready")
            self.status_icon.setStyleSheet("color : green;")
        else:
            self.status_icon.setText("Not Ready")
            self.status_icon.setStyleSheet("color : red;")

    @pyqtSlot()
    def fetch_started(self) -> None:
        """Change the text of the "Fetch Data" button to "Cancel", and turn the
        self.progress_outer and self.progress_inner widgets into progress bars.
        """
        logging.debug("Signal received: fetch_started")
        self.fetch_button_wrapper.button.setText("Cancel")
        self.fetch_button_wrapper.button.clicked.disconnect(self.fetch_data)
        self.fetch_button_wrapper.button.clicked.connect(self.cancel_fetch)
        # The progress bars are empty widgets by default, so we need to
        # replace them with progress bars
        self.progress_outer = QProgressBar(self.progress_outer)
        self.progress_inner = QProgressBar(self.progress_inner)

    @pyqtSlot(int)
    def outer_progress_changed(
        self, current_value: int, max_value: int
    ) -> None:
        """Set the value of the outer progress bar."""
        logging.debug("Signal received: progress_bar_outer")
        self.progress_outer.setMaximum(max_value)
        self.progress_outer.setValue(current_value)

    @pyqtSlot(int)
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
        """Change the text of the "Cancel" button back to "Fetch Data", and
        disconnect the signal from the slot.
        """
        logging.debug("Signal received: cancel_fetch")
        self.fetch_button_wrapper.button.setText("Fetch Data")
        self.fetch_button_wrapper.button.clicked.disconnect(self.cancel_fetch)
        self.fetch_button_wrapper.button.clicked.connect(self.fetch_data)
        # Reset progress bars to empty widgets
        self.progress_outer = QWidget()
        self.progress_inner = QWidget()

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
        self.async_runner = AsyncRunner(scraper)
        self.connect_scraper_signals()


if __name__ == "__main__":
    # Reset logging
    logging.root.handlers = []
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication([])
    ex = App()
    ex.show()
    app.exec_()
