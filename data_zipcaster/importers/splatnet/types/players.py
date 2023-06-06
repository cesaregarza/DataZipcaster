from typing import Literal

from json_keys import players as players_keys
from typing_extensions import NotRequired, TypedDict


class GearItemDict(TypedDict):
    players_keys.PRIMARY_ABILITY: str
    players_keys.ADDITIONAL_ABILITIES: list[str]


class GearDict(TypedDict):
    players_keys.HEADGEAR: GearItemDict
    players_keys.CLOTHING: GearItemDict
    players_keys.SHOES: GearItemDict


class PlayerDict(TypedDict):
    players_keys.NAME: str
    players_keys.ME: bool
    players_keys.PLAYER_NUMBER: NotRequired[str]
    players_keys.SPLASHTAG: str
    players_keys.WEAPON_NAME: str
    players_keys.WEAPON_ID: int
    players_keys.SUB_NAME: str
    players_keys.SPECIAL_NAME: str
    players_keys.INKED: int
    players_keys.SPECIES: Literal["inkling", "octoling"]
    players_keys.SCOREBOARD_POSITION: int
    players_keys.GEAR: GearDict
    players_keys.DISCONNECTED: bool
    players_keys.KILLS_OR_ASSISTS: NotRequired[int]
    players_keys.ASSISTS: NotRequired[int]
    players_keys.KILLS: NotRequired[int]
    players_keys.DEATHS: NotRequired[int]
    players_keys.SPECIALS: NotRequired[int]
    players_keys.SIGNALS: NotRequired[int | None]
    players_keys.TOP_500_CROWN: NotRequired[bool]
