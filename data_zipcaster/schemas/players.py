from typing import Literal

from typing_extensions import NotRequired, TypedDict

from data_zipcaster.schemas.typing import BadgeType


class GearItemDict(TypedDict):
    name: str
    brand: str
    primary_ability: str
    additional_abilities: list[str]


class GearDict(TypedDict):
    headgear: GearItemDict
    clothing: GearItemDict
    shoes: GearItemDict


class NameplateDict(TypedDict):
    badges: BadgeType
    text_color: str
    background_id: str


class PlayerDict(TypedDict):
    name: str
    npln_id: str
    me: bool
    player_number: NotRequired[str]
    splashtag: str
    nameplate: NameplateDict
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
    crown: NotRequired[bool]
    crown_type: NotRequired[Literal["DRAGON", "DOUBLE_DRAGON"]]
