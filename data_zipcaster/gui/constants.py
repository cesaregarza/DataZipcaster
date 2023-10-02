from enum import Enum, auto


class GUIStates(Enum):
    """The states the UI can be in.

    INIT: The UI is initializing.
    NOT_READY: The UI is ready to be configured.
    READY: The UI is ready to fetch data.
    TESTING: The UI is testing the tokens.
    FETCHING: The UI is fetching data.
    CANCELLING: The UI is cancelling the fetch.
    """

    INIT = auto()
    NOT_READY = auto()
    READY = auto()
    TESTING = auto()
    FETCHING = auto()
    CANCELLING = auto()
    DATA_READY = auto()
    CONTINUOUS = auto()
