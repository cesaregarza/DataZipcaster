from typing import Optional

from pydantic import BaseModel, validator

from data_zipcaster.models.main.typing import (
    AbilityType,
    BadgeType,
    CrownType,
    SpeciesType,
    StackableAbilityType,
)


class GearItem(BaseModel):
    name: str
    brand: str
    primary_ability: AbilityType
    additional_abilities: list[StackableAbilityType | None]

    @validator("additional_abilities")
    def validate_additional_abilities(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("additional_abilities must have 3 elements")

        return v


class Gear(BaseModel):
    headgear: GearItem
    clothing: GearItem
    shoes: GearItem


class NamePlate(BaseModel):
    badges: BadgeType
    text_color: str
    background_id: str

    @validator("text_color")
    def validate_text_color(cls, v):
        if v[0] != "#":
            raise ValueError("text_color must start with #")

        if len(v) != 9:
            raise ValueError("text_color must have rrggbbaa format")

        if not all(c in "0123456789abcdef" for c in v[1:]):
            raise ValueError("text_color must have rrggbbaa format")

        return v


class Player(BaseModel):
    name: str
    npln_id: str
    me: bool
    player_number: Optional[str] = None
    splashtag: str
    nameplate: NamePlate
    weapon_name: str
    weapon_id: int
    sub_name: str
    special_name: str
    inked: int
    species: SpeciesType
    scoreboard_position: int
    gear: Gear
    disconnected: bool
    kills_or_assists: Optional[int] = None
    assists: Optional[int] = None
    kills: Optional[int] = None
    deaths: Optional[int] = None
    specials: Optional[int] = None
    signals: Optional[int] = None
    crown: Optional[int] = None
    crown_type: Optional[CrownType] = None