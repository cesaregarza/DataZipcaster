import logging
import os
import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from data_zipcaster import __version__
from data_zipcaster.gui.utils import SplatNet_Scraper_Wrapper
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        ui_path = pathlib.Path(__file__).parent / "ui" / "main.ui"
        uic.loadUi(str(ui_path), self)
        self.cwd = os.getcwd()
        self.setup_ui()
        self.scraper: SplatNet_Scraper_Wrapper | None = None
        logger.debug("App initialized")

    def setup_ui(self) -> None:
        """Set up the UI."""
        logger.debug("Setting up UI")
        self.setWindowTitle("Data Zipcaster")
        self.set_icon()
        self.version_label.setText(f"v.{__version__}")

        self.setup_buttons()
        self.setup_sliders_spinboxes()
        self.check_config_path_on_init()

        # Disable Salmon Run for now with a tooltip
        self.salmon_check.setEnabled(False)
        self.salmon_check.setToolTip("Salmon Run is not supported yet")

    def setup_buttons(self) -> None:
        """Set up the buttons. Disable buttons initially if necessary."""
        logger.debug("Setting up buttons")
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

    def setup_sliders_spinboxes(self) -> None:
        """Set up the sliders and spinboxes."""
        logger.debug("Setting up sliders and spinboxes")
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

    def set_icon(self) -> None:
        """Set the window icon."""
        logger.debug("Setting window icon")
        logo_path = (
            pathlib.Path(__file__).parent.parent / "assets" / "dz_logo.png"
        )
        icon = QIcon(str(logo_path))
        self.setWindowIcon(icon)

    def check_config_path_on_init(self) -> None:
        """Check if a config file exists in the current working directory.

        If a config file exists, enable the "Test Tokens" button.
        """
        logger.debug("Checking for config file")
        config_path = pathlib.Path(self.cwd) / "config.ini"
        if config_path.exists():
            logger.debug("Config file found")
            self.config_path_text.setText(str(config_path))
            self.load_config()

    def load_config(self) -> None:
        """Load a config file."""
        logger.info("Attempting to load config file")
        config_path = self.config_path_text.text()
        if not config_path:
            logger.error("No config file selected")
            self.show_error("Please select a config file first.")
            return
        try:
            logger.debug("Loading config file")
            scraper = SplatNet_Scraper_Wrapper.from_config(config_path)
        except KeyError:
            logger.error("Config file is invalid")
            self.show_error(
                "The config file is invalid. Please make sure the file is "
                "correctly formatted."
            )
            return
        self.set_scraper(scraper)

    def open_file_dialog(self) -> None:
        """Open a file dialog to select a config file."""
        logger.debug("Opening file dialog")
        config_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select config file",
            self.cwd,
            "Config files (*.ini)",
        )
        if config_path:
            logger.debug("Config file selected")
            self.config_path_text.setText(config_path)
            self.cwd = os.path.dirname(config_path)
            self.test_tokens_button_wrapper.set_enabled(True)
            self.load_config_button_wrapper.set_enabled(True)
        else:
            logger.debug("No config file selected")

    def test_tokens(self) -> None:
        """Test the tokens in the config file."""
        logger.info("Testing tokens")
        if self.scraper is None:
            logger.error("No scraper found")
            return
        self.scraper.test_tokens()

    def show_info(self, msg: str, window_title: str = "Info") -> None:
        """Show an info message.

        Args:
            msg (str): The message to show.
            window_title (str): The title of the window. Defaults to "Info".
        """
        logger.debug("Showing info message")
        info = QMessageBox()
        info.setIcon(QMessageBox.Information)
        info.setText("Info")
        info.setInformativeText(msg)
        info.setWindowTitle(window_title)
        info.exec_()

    def show_error(self, msg: str, window_title: str = "Error") -> None:
        """Show an error message.

        Args:
            msg (str): The message to show.
            window_title (str): The title of the window. Defaults to "Error".
        """
        logger.debug("Showing error message")
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Error")
        error.setInformativeText(msg)
        error.setWindowTitle(window_title)
        error.exec_()

    def set_scraper(self, scraper: SplatNet_Scraper_Wrapper) -> None:
        """Set the scraper and make changes that depend on it.

        Args:
            scraper (SplatNet_Scraper_Wrapper): The scraper to set.
        """
        logger.debug("Setting scraper")
        self.scraper = scraper
        self.test_tokens_button_wrapper.set_enabled(True)
        self.load_config_button_wrapper.set_enabled(True)
        self.connect_signals()

    def connect_signals(self) -> None:
        """Connect signals to slots."""
        logger.debug("Connecting signals")
        self.scraper.testing_started.connect(self.testing_started)
        self.scraper.testing_finished.connect(self.testing_finished)

    @pyqtSlot()
    def testing_started(self) -> None:
        """Disable the "Test Tokens" button and change its text to "Testing..."""
        logger.debug("Signal received: testing_started")
        self.test_tokens_button_wrapper.set_enabled(False)
        self.test_tokens_button_wrapper.button.setText("Testing...")

    @pyqtSlot(bool)
    def testing_finished(self, success: bool) -> None:
        """Enable the "Test Tokens" button and change its text to "Test Tokens" """
        logger.debug("Signal received: testing_finished")
        self.test_tokens_button_wrapper.set_enabled(True)
        self.test_tokens_button_wrapper.button.setText("Test Tokens")
        if success:
            self.show_info("Tokens are valid!")
        else:
            self.show_error("Tokens are invalid!")


if __name__ == "__main__":
    app = QApplication([])
    ex = App()
    ex.show()
    app.exec_()
