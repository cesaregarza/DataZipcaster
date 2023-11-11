from __future__ import annotations

import logging
from typing import Callable, TypeAlias

from PyQt5.QtCore import QObject, pyqtSlot

from data_zipcaster.gui.base_class import BaseClass
from data_zipcaster.gui.constants import GUIStates
from data_zipcaster.gui.ui_manager import UIManager

StateFunc: TypeAlias = Callable[["StateManager"], None]
StateMap: TypeAlias = dict[GUIStates, StateFunc]
StateTransitionMap: TypeAlias = dict[tuple[GUIStates, GUIStates], StateFunc]


class StateManager(QObject):
    """Class to manage the state of the application."""

    def __init__(self, base: BaseClass, ui_manager: UIManager) -> None:
        super().__init__()
        self.base = base
        self.ui_manager = ui_manager

    @property
    def state(self) -> GUIStates:
        return self.base.state

    @state.setter
    def state(self, value: GUIStates) -> None:
        self.base.state = value

    @property
    def state_map(self) -> StateMap:
        return {
            GUIStates.NOT_READY: self.state_not_ready,
            GUIStates.READY: self.state_ready,
            GUIStates.TESTING: self.state_testing,
            GUIStates.FETCHING: self.state_fetching,
            GUIStates.CANCELLING: self.state_cancelling,
            GUIStates.DATA_READY: self.state_data_ready,
            GUIStates.CONTINUOUS: self.state_continuous,
        }

    @property
    def state_transition_map(self) -> StateTransitionMap:
        return {
            (
                GUIStates.CONTINUOUS,
                GUIStates.FETCHING,
            ): self.continuous_to_fetching,
        }

    @pyqtSlot(GUIStates)
    def state_changed(self, new_state: GUIStates) -> None:
        logging.debug("Signal received: state_changed")
        logging.debug(
            "Attempting to change state from %s to %s",
            self.base.state.name,
            new_state.name,
        )
        if self.base.state == new_state:
            logging.debug("State is already %s, doing nothing", new_state.name)
            return

        if (self.base.state, new_state) in self.state_transition_map:
            logging.debug("Transitioning state")
            self.state_transition_map[(self.base.state, new_state)]()
            return

        logging.debug("No transition found, changing state")

        self.base.state = new_state
        self.state_map[new_state]()

    def state_transition(
        self, old_state: GUIStates, new_state: GUIStates
    ) -> bool:
        logging.debug(
            "Transitioning from %s to %s", old_state.name, new_state.name
        )
        transition_map: StateTransitionMap = {
            (
                GUIStates.CONTINUOUS,
                GUIStates.FETCHING,
            ): self.continuous_to_fetching,
        }
        if (old_state, new_state) in transition_map:
            transition_map[(old_state, new_state)]()
            return True
        return False

    ### State functions ###
    # These functions should only make changes to the UI, and should not
    # change the state of the application. If you need to change the state,
    # use a state transition function instead.
    def state_not_ready(self) -> None:
        logging.info("State changed to NOT_READY")
        base = self.base
        base.ready = False

        base.status_icon_label.setText("Not Ready")
        base.status_icon_label.setStyleSheet("color : red;")
        base.fetch_button_wrapper.set_enabled(False)
        base.view_button_wrapper.set_enabled(False)
        base.export_all_button_wrapper.set_enabled(False)
        base.test_tokens_button_wrapper.set_enabled(True)
        base.test_tokens_button.setText("Test Tokens")

    def state_ready(self) -> None:
        logging.info("State changed to READY")
        base = self.base
        base.ready = True

        base.status_icon_label.setText("Ready")
        base.status_icon_label.setStyleSheet("color : green;")
        base.fetch_button_wrapper.set_enabled(True)
        base.view_button_wrapper.set_enabled(False)
        base.export_all_button_wrapper.set_enabled(False)
        base.test_tokens_button_wrapper.set_enabled(True)
        base.test_tokens_button.setText("Test Tokens")
        base.fetch_button.setText("Fetch")
        self.ui_manager.hide_progress_bars()
        self.ui_manager.set_checkboxes_state(enabled=True, all_checkboxes=True)
        base.limit_slider_spinbox.set_enabled(True)

    def state_testing(self) -> None:
        logging.info("State changed to TESTING")
        base = self.base
        base.test_tokens_button_wrapper.set_enabled(False)
        base.test_tokens_button.setText("Testing...")

    def state_fetching(self) -> None:
        logging.info("State changed to FETCHING")
        base = self.base
        base.fetch_button.setText("Cancel")
        self.ui_manager.show_progress_bars()
        self.ui_manager.set_checkboxes_state(enabled=False, all_checkboxes=True)
        base.limit_slider_spinbox.set_enabled(False)
        base.interval_slider_spinbox.set_enabled(False)

    def state_cancelling(self) -> None:
        logging.info("State changed to CANCELLING")
        base = self.base
        base.fetch_button.setText("Cancelling...")
        base.fetch_button.setEnabled(False)

    def state_data_ready(self) -> None:
        logging.info("State changed to DATA_READY")
        self.state_ready()

    def state_continuous(self) -> None:
        logging.info("State changed to CONTINUOUS")
        base = self.base
        base.fetch_button.setText("Stop")
        self.ui_manager.show_progress_bars()
        base.fetch_button_wrapper.set_enabled(True)
        base.view_button_wrapper.set_enabled(False)
        base.export_all_button_wrapper.set_enabled(False)
        base.test_tokens_button_wrapper.set_enabled(False)
        base.test_tokens_button.setText("Test Tokens")
        self.ui_manager.set_checkboxes_state(enabled=False, all_checkboxes=True)

    ### State transition functions ###
    # These functions should handle more complex state transitions, such as
    # transitioning from CONTINUOUS to FETCHING. Try to keep UI changes in
    # state functions, with minimal UI changes in state transition functions.
    def continuous_to_fetching(self) -> None:
        """Transition function for CONTINUOUS to FETCHING.

        Does not actually change the state, but applies all the changes that
        would be made if the state was changed to FETCHING. This is because the
        fetch button will attempt to change the state to FETCHING, but we want
        to keep the state as CONTINUOUS.
        """
        logging.info("Transitioning from CONTINUOUS to FETCHING")
        # This signal should only be emitted when fetch_data is called, so
        # we can assume that the state is READY
        self.state_fetching()
