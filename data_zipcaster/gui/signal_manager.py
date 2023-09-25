import logging
import pathlib

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QIcon

from data_zipcaster import __version__
from data_zipcaster.gui.base_class import BaseClass


class SignalManager(QObject):
    """Class to manage Signals. This is mostly just a wrapper around the Signals
    to make them easier to read and write.
    """

    def __init__(self, main_window: BaseClass) -> None:
        self.main_window = main_window
        self.setup_signals()

    def setup_signals(self) -> None:
        logging.info("Setting up signals")

    @pyqtSlot()
    def testing_started(self) -> None:
        logging.info("Testing tokens started")
        main = self.main_window
        main.test_tokens_button_wrapper.set_enabled(False)
        main.test_tokens_button.setText("Testing...")

    @pyqtSlot(bool)
    def testing_finished(self, success: bool) -> None:
        logging.info("Testing tokens finished")
        main = self.main_window
        main.test_tokens_button_wrapper.set_enabled(True)
        main.test_tokens_button.setText("Test Tokens")
        main.ready_signal.emit(success)

        if success:
            # Save the config if the tokens are valid
            path = pathlib.Path(main.config_path_text.text())
            if path.exists():
                main.scraper.save_config(str(path))
        else:
            main.show_error(
                "Tokens are invalid. Please check your config file."
            )
        main.fetch_button_wrapper.set_enabled(success)
