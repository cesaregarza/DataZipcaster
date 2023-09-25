import logging
import pathlib

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon

from data_zipcaster import __version__
from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"


class UIManager(QObject):
    """Class to manage the UI elements. This is mostly just a wrapper around
    the UI elements to make them easier to read and write.
    """

    def __init__(self, main_window: BaseClass) -> None:
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the UI elements."""
        logging.info("Setting up UI elements")
        main = self.main_window
        main.setWindowTitle("Data Zipcaster")
        self.set_icon()
        main.version_label.setText(f"v.{__version__}")

        self.setup_buttons()
        self.setup_sliders_spinboxes()
        self.setup_checkboxes()

        # Hide the progress bars
        main.progress_outer.hide()
        main.progress_inner.hide()

        # Disable Salmon Run for now with the tooltip
        main.salmon_check.setEnabled(False)
        main.salmon_check.setToolTip("Salmon Run is not supported yet")

    def set_icon(self) -> None:
        """Sets the icon for the window."""
        logging.info("Setting window icon")
        main = self.main_window
        logo_path = ASSETS_PATH / "dz_logo.png"
        icon = QIcon(str(logo_path))
        main.setWindowIcon(icon)

    def setup_buttons(self) -> None:
        logging.info("Setting up buttons")
        main = self.main_window
        main.fetch_button_wrapper = Button(
            main.fetch_button,
            enabled_tooltip="Fetch data",
            disabled_tooltip="Please select at least one data source first",
            enabled=False,
        )
        main.view_button_wrapper = Button(
            main.view_button,
            enabled_tooltip="View data",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        main.export_all_button_wrapper = Button(
            main.export_all_button,
            enabled_tooltip="Export all data",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        main.config_path_button_wrapper = Button(
            main.config_path_button,
            enabled_tooltip="Select config file",
        )
        main.new_session_button_wrapper = Button(
            main.new_session_button,
            enabled_tooltip="Fetch a new session token",
        )
        main.test_tokens_button_wrapper = Button(
            main.test_tokens_button,
            enabled_tooltip="Test tokens",
            disabled_tooltip="Please load a config file first",
            enabled=False,
        )
        main.load_config_button_wrapper = Button(
            main.load_config_button,
            enabled_tooltip="Load config file",
            disabled_tooltip="Please select a config file first",
            enabled=False,
        )

        # Connect buttons to functions
        # main.config_path_button.clicked.connect(main.open_file_dialog)
        # main.load_config_button.clicked.connect(main.load_config)
        # main.test_tokens_button.clicked.connect(main.test_tokens)
        # main.fetch_button.clicked.connect(main.fetch_data)

    def setup_sliders_spinboxes(self) -> None:
        logging.info("Setting up sliders and spinboxes")
        main = self.main_window
        main.limit_slider_spinbox = SliderSpinbox(
            main.limit_slider,
            main.limit_spinbox,
            enabled_tooltip="Limit",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )
        main.interval_slider_spinbox = SliderSpinbox(
            main.interval_slider,
            main.interval_spinbox,
            enabled_tooltip="Interval",
            disabled_tooltip="Please fetch data first",
            enabled=False,
        )

        # Connect sliders and spinboxes to functions
        main.interval_slider_spinbox.link_checkbox(main.continuous_check)

    def setup_checkboxes(self) -> None:
        logging.info("Setting up checkboxes")
        # main = self.main_window
        # for checkbox in main.checkboxes:
        # checkbox.stateChanged.connect(main.checkboxes_changed)

    def show_progress_bars(self) -> None:
        """Show the progress bars."""
        logging.info("Showing progress bars")
        main = self.main_window
        main.widget_outer.hide()
        main.widget_inner.hide()
        main.progress_outer.setValue(0)
        main.progress_inner.setValue(0)
        main.progress_outer.show()
        main.progress_inner.show()

    def hide_progress_bars(self) -> None:
        """Hide the progress bars."""
        logging.info("Hiding progress bars")
        main = self.main_window
        main.progress_outer.hide()
        main.progress_inner.hide()
        main.widget_outer.show()
        main.widget_inner.show()
