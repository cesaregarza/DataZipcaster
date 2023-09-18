import numpy as np
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
    QCheckBox,
)


class Button:
    def __init__(
        self,
        button: QPushButton,
        enabled: bool = True,
        enabled_tooltip: str = "",
        disabled_tooltip: str | None = None,
    ) -> None:
        self.button = button
        self.enabled_tooltip = enabled_tooltip
        self.disabled_tooltip = disabled_tooltip
        self.set_enabled(enabled)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button.

        A helper function to enable or disable the button, and change the
        tooltip accordingly.

        Args:
            enabled (bool): Whether to enable or disable the button.
        """
        self.button.setEnabled(enabled)

        if self.disabled_tooltip is None:
            self.button.setToolTip(self.enabled_tooltip)
        else:
            self.button.setToolTip(
                self.enabled_tooltip if enabled else self.disabled_tooltip
            )


class SliderSpinbox:
    def __init__(
        self,
        slider: QSlider,
        spinbox: QSpinBox,
        enabled: bool = True,
        enabled_tooltip: str = "",
        disabled_tooltip: str | None = None,
    ) -> None:
        self.slider = slider
        self.spinbox = spinbox
        self.enabled_tooltip = enabled_tooltip
        self.disabled_tooltip = disabled_tooltip
        self.set_enabled(enabled)
        self.link_slider_spinbox()

    def link_slider_spinbox(self) -> None:
        """Link the slider and spinbox together.

        This sets the slider and spinbox to the same minimum, maximum, and
        value, based on the spinbox's defined values. It also connects the
        valueChanged signals of the slider and spinbox together, so that
        changing one will change the other.
        """

        self.slider.setMinimum(self.spinbox.minimum())
        self.slider.setMaximum(self.spinbox.maximum())
        self.slider.setValue(self.spinbox.value())

        self.slider.valueChanged.connect(self.spinbox.setValue)
        self.spinbox.valueChanged.connect(self.slider.setValue)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the slider and spinbox.

        A helper function to enable or disable the slider and spinbox, and
        change the tooltip accordingly.

        Args:
            enabled (bool): Whether to enable or disable the slider and spinbox.
        """
        self.slider.setEnabled(enabled)
        self.spinbox.setEnabled(enabled)

        tooltip = self.enabled_tooltip if enabled else self.disabled_tooltip
        self.slider.setToolTip(tooltip)
        self.spinbox.setToolTip(tooltip)

    def link_checkbox(self, checkbox: QCheckBox) -> None:
        """Link the slider and spinbox to a checkbox.

        This sets the SliderSpinbox to be enabled or disabled based on the
        state of the checkbox, and connects the stateChanged signal of the
        checkbox to the set_enabled method of the SliderSpinbox.

        Args:
            checkbox (QCheckBox): The checkbox to link to.
        """
        checkbox.stateChanged.connect(
            lambda state: self.set_enabled(state == Qt.Checked)
        )
