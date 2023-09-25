import logging
import os
import pathlib

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from data_zipcaster.gui.widget_wrappers import Button, SliderSpinbox


class BaseClass(QMainWindow):
    """Base class for the UI. Mostly just adds type hints to the UI elements."""

    # Labels
    version_label: QLabel
    status_icon_label: QLabel

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
