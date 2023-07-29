from typing import Literal, TypeAlias

FlagType: TypeAlias = Literal[
    "salmon",
    "xbattle",
    "turf",
    "anarchy",
    "private",
    "challenge",
]
FLAG_MAP: dict[FlagType, str] = {
    "xbattle": "Xbattle",
    "anarchy": "Anarchy",
    "turf": "Turf War",
    "private": "Private Battle",
    "challenge": "Challenge",
    "salmon": "Salmon Run",
}

FLAG_LIST: list[FlagType] = [
    "salmon",
    "xbattle",
    "turf",
    "anarchy",
    "private",
    "challenge",
]
