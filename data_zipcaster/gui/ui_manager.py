import logging
import pathlib

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QIcon

from data_zipcaster import __version__
from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"


class UIManager(QObject):
    """Class to manage the UI elements. This is mostly just a wrapper around
    the UI elements to make them easier to read and write.
    """

    def __init__(self, base: BaseClass) -> None:
        self.base = base
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the UI elements."""
        logging.info("Setting up UI elements")
        base = self.base
        base.setWindowTitle("Data Zipcaster")
        self.set_icon()
        base.version_label.setText(f"v.{__version__}")

        self.setup_buttons()
        self.setup_sliders_spinboxes()
        self.setup_checkboxes()
        self.hide_progress_bars()

        # Disable Salmon Run for now with the tooltip
        base.salmon_check.setEnabled(False)
        base.salmon_check.setToolTip("Salmon Run is not supported yet")

    def set_icon(self) -> None:
        """Sets the icon for the window."""
        logging.info("Setting window icon")
        base = self.base
        logo_path = ASSETS_PATH / "dz_logo.png"
        icon = QIcon(str(logo_path))
        base.setWindowIcon(icon)

    def setup_buttons(self) -> None:
        logging.info("Setting up buttons")
        base = self.base
        base.fetch_button_wrapper = Button(
            base.fetch_button,
            enabled_tooltip="Fetch data",
            disabled_tooltip="Please select at least one data source first",
            enabled=False,
        )
        base.view_button_wrapper = Button(
            base.view_button,
            enabled_tooltip="View data",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        base.export_all_button_wrapper = Button(
            base.export_all_button,
            enabled_tooltip="Export all data",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        base.config_path_button_wrapper = Button(
            base.config_path_button,
            enabled_tooltip="Select config file",
        )
        base.new_session_button_wrapper = Button(
            base.new_session_button,
            enabled_tooltip="Fetch a new session token",
        )
        base.test_tokens_button_wrapper = Button(
            base.test_tokens_button,
            enabled_tooltip="Test tokens",
            disabled_tooltip="Please load a config file first",
            enabled=False,
        )
        base.load_config_button_wrapper = Button(
            base.load_config_button,
            enabled_tooltip="Load config file",
            disabled_tooltip="Please select a config file first",
            enabled=False,
        )

        # Connect buttons to functions
        # base.config_path_button.clicked.connect(base.open_file_dialog)
        # base.load_config_button.clicked.connect(base.load_config)
        # base.test_tokens_button.clicked.connect(base.test_tokens)
        # base.fetch_button.clicked.connect(base.fetch_data)

    def setup_sliders_spinboxes(self) -> None:
        logging.info("Setting up sliders and spinboxes")
        base = self.base
        base.limit_slider_spinbox = SliderSpinbox(
            base.limit_slider,
            base.limit_spinbox,
            enabled_tooltip="Limit",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        base.interval_slider_spinbox = SliderSpinbox(
            base.interval_slider,
            base.interval_spinbox,
            enabled_tooltip="Interval",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )

        # Connect sliders and spinboxes to functions
        base.interval_slider_spinbox.link_checkbox(base.continuous_check)

    def setup_checkboxes(self) -> None:
        logging.info("Setting up checkboxes")
        # base = self.base_window
        # for checkbox in base.checkboxes:
        # checkbox.stateChanged.connect(base.checkboxes_changed)

    def show_progress_bars(self) -> None:
        """Show the progress bars."""
        logging.info("Showing progress bars")
        base = self.base
        base.widget_outer.hide()
        base.widget_inner.hide()
        base.progress_outer.setValue(0)
        base.progress_inner.setValue(0)
        base.progress_outer.show()
        base.progress_inner.show()

    def hide_progress_bars(self) -> None:
        """Hide the progress bars."""
        logging.info("Hiding progress bars")
        base = self.base
        base.progress_outer.hide()
        base.progress_inner.hide()
        base.widget_outer.show()
        base.widget_inner.show()

    @pyqtSlot(int, int)
    def outer_progress_changed(
        self, current_value: int, max_value: int
    ) -> None:
        """Set the value of the outer progress bar."""
        logging.debug("Signal received: progress_bar_outer")
        base = self.base
        base.progress_outer.setMaximum(max_value)
        base.progress_outer.setValue(current_value)

    @pyqtSlot(int, int)
    def inner_progress_changed(
        self, current_value: int, max_value: int
    ) -> None:
        """Set the value of the inner progress bar."""
        logging.debug("Signal received: progress_bar_inner")
        base = self.base
        base.progress_inner.setMaximum(max_value)
        base.progress_inner.setValue(current_value)
