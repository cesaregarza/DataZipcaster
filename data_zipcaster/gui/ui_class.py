from PyQt5.QtWidgets import (
    QApplication,
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


class UIBaseClass(QMainWindow):
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
