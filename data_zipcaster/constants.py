from __future__ import annotations

import base64
import json
import uuid
from typing import TypedDict, cast

from data_zipcaster import __version__

DEFAULT_USER_AGENT = f"data_zipcaster/{__version__}"


# From S3S
class NAMESPACES:
    STATINK = uuid.UUID("b3a2dbf5-2c09-4792-b78c-00b548b70aeb")


class Mode(TypedDict):
    name: str
    key: str
    properties: list[str]
    _id: int


class MODES:
    TURF_WAR = Mode(
        name="Turf War", key="regular", properties=["turf_war"], _id=1
    )
    ANARCHY_SERIES = Mode(
        name="Anarchy Series",
        key="bankara_challenge",
        properties=["anarchy"],
        _id=2,
    )
    X_BATTLE = Mode(
        name="X Battle", key="xbattle", properties=["xbattle"], _id=3
    )
    PRIVATE_BATTLE = Mode(
        name="Private Battle", key="private", properties=["private"], _id=5
    )
    ANARCHY_OPEN = Mode(
        name="Anarchy Open", key="bankara_open", properties=["anarchy"], _id=51
    )
    SPLATFEST = Mode(
        name="Splatfest",
        key="splatfest_open",
        properties=["splatfest", "turf_war"],
        _id=6,
    )
    SPLATFEST_PRO = Mode(
        name="Splatfest Pro",
        key="splatfest_challenge",
        properties=["splatfest", "turf_war", "pro"],
        _id=7,
    )
    SPLATFEST_TRICOLOR = Mode(
        name="Splatfest Tricolor",
        key="splatfest_open",
        properties=["splatfest", "turf_war", "tricolor"],
        _id=8,
    )

    @staticmethod
    def get_modes() -> list[Mode]:
        return [
            getattr(MODES, attr)
            for attr in dir(MODES)
            if isinstance(getattr(MODES, attr), dict)
        ]

    @staticmethod
    def get_mode_by_id(mode_id: int | str) -> Mode:
        if isinstance(mode_id, str):
            mode_id = int(mode_id)

        modes = MODES.get_modes()
        for mode in modes:
            if mode["_id"] == mode_id:
                return mode
        raise ValueError(f"Invalid mode ID: {mode_id}")

    @staticmethod
    def get_mode_by_key(mode_key: str) -> Mode:
        modes = MODES.get_modes()
        for mode in modes:
            if mode["key"] == mode_key:
                return mode
        raise ValueError(f"Invalid mode key: {mode_key}")

    @staticmethod
    def get_mode_by_name(mode_name: str) -> Mode:
        modes = MODES.get_modes()
        for mode in modes:
            if mode["name"] == mode_name:
                return mode
        raise ValueError(f"Invalid mode name: {mode_name}")


RANKS = [
    "C-",
    "C",
    "C+",
    "B-",
    "B",
    "B+",
    "A-",
    "A",
    "A+",
    "S",
    "S+",
]
