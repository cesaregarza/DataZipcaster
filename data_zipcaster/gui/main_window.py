import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
    QCheckBox,
    QProgressBar,
)

from data_zipcaster import __version__
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        ui_path = pathlib.Path(__file__).parent / "ui" / "main.ui"
        uic.loadUi(str(ui_path), self)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the UI."""
        self.setWindowTitle("Data Zipcaster")
        self.set_icon()
        self.version_label.setText(f"v.{__version__}")

        self.setup_buttons()
        self.setup_sliders_spinboxes()

        # Disable Salmon Run for now with a tooltip
        self.salmon_check.setEnabled(False)
        self.salmon_check.setToolTip("Salmon Run is not supported yet")


    def setup_buttons(self) -> None:
        """Set up the buttons. Disable buttons initially if necessary."""
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

    def setup_sliders_spinboxes(self) -> None:
        """Set up the sliders and spinboxes."""
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
        self.interval_slider_spinbox.link_checkbox(self.continuous_check)

    def set_icon(self) -> None:
        logo_path = (
            pathlib.Path(__file__).parent.parent / "assets" / "dz_logo.png"
        )
        icon = QIcon(str(logo_path))
        self.setWindowIcon(icon)


if __name__ == "__main__":
    app = QApplication([])
    ex = App()
    ex.show()
    app.exec_()
