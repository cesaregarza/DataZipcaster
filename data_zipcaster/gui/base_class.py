import logging
import os
import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from data_zipcaster.gui.constants import GUIStates
from data_zipcaster.gui.utils import SplatNet_Scraper_Wrapper
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox


class BaseClass(QMainWindow):
    """Base class for the UI. Mostly just adds type hints to the UI elements."""

    # Labels
    version_label: QLabel
    status_icon_label: QLabel
    status_label: QLabel

    # Progress bars
    progress_outer: QProgressBar
    progress_inner: QProgressBar

    # Checkboxes
    anarchy_check: QCheckBox
    private_check: QCheckBox
    turf_check: QCheckBox
    x_check: QCheckBox
    challenge_check: QCheckBox
    salmon_check: QCheckBox
    continuous_check: QCheckBox

    # Buttons
    fetch_button: QPushButton
    view_button: QPushButton
    export_all_button: QPushButton
    config_path_button: QPushButton
    new_session_button: QPushButton
    test_tokens_button: QPushButton
    load_config_button: QPushButton

    # Sliders and spinboxes
    limit_slider: QSlider
    limit_spinbox: QSpinBox
    interval_slider: QSlider
    interval_spinbox: QSpinBox

    # Other
    config_path_text: QLineEdit
    widget_outer: QWidget
    widget_inner: QWidget
    scraper: SplatNet_Scraper_Wrapper
    state: GUIStates
    ready: bool
    data: dict

    # Button wrappers
    fetch_button_wrapper: Button
    view_button_wrapper: Button
    export_all_button_wrapper: Button
    config_path_button_wrapper: Button
    new_session_button_wrapper: Button
    test_tokens_button_wrapper: Button
    load_config_button_wrapper: Button

    # Slider and spinbox wrappers
    limit_slider_spinbox: SliderSpinbox
    interval_slider_spinbox: SliderSpinbox

    # Signals
    fetching_started = pyqtSignal()
    cancel_signal = pyqtSignal()
    set_scraper_signal = pyqtSignal(SplatNet_Scraper_Wrapper)
    state_changed_signal = pyqtSignal(GUIStates)

    # Properties
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

    @property
    def all_checkboxes(self) -> list[QCheckBox]:
        return self.checkboxes + [self.continuous_check]

    @property
    def cwd(self) -> str:
        if not hasattr(self, "_cwd"):
            self._cwd = pathlib.Path.cwd()
        return str(self._cwd)

    @cwd.setter
    def cwd(self, value: str) -> None:
        self._cwd = pathlib.Path(value)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state = GUIStates.INIT
        self.ready = False
        self.data = {}

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
