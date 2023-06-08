from typing import Literal

from typing_extensions import NotRequired, TypedDict


class GearItemDict(TypedDict):
    name: str
    brand: str
    primary_ability: str
    additional_abilities: list[str]


class GearDict(TypedDict):
    headgear: GearItemDict
    clothing: GearItemDict
    shoes: GearItemDict


class PlayerDict(TypedDict):
    name: str
    me: bool
    player_number: NotRequired[str]
    splashtag: str
    weapon_name: str
    weapon_id: int
    sub_name: str
    special_name: str
    inked: int
    species: Literal["inkling", "octoling"]
    scoreboard_position: int
    gear: GearDict
    disconnected: bool
    kills_or_assists: NotRequired[int]
    assists: NotRequired[int]
    kills: NotRequired[int]
    deaths: NotRequired[int]
    specials: NotRequired[int]
    signals: NotRequired[int | None]
    top_500_crown: NotRequired[bool]
