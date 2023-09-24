from enum import Enum, auto


class GUIStates(Enum):
    """Enum for GUI states"""

    INIT = auto()
    READY = auto()
    TESTING = auto()
    FETCHING = auto()
    CANCELLING = auto()
