from typing import Optional

from pydantic import BaseModel, validator

from data_zipcaster.models.main.typing import (
    AbilityType,
    BadgeType,
    CrownType,
    SpeciesType,
    StackableAbilityType,
)

__all__ = [
    "GearItem",
    "Gear",
    "Nameplate",
    "Player",
]


class GearItem(BaseModel):
    """The model for a piece of gear.

    Fields:
        - name (str): The name of the gear.
        - brand (str): The brand of the gear.
        - primary_ability (AbilityType): The primary ability of the gear.
        - additional_abilities (list[StackableAbilityType | None]): The
            additional abilities of the gear. This is a list of 3 elements,
            where each element is either a StackableAbilityType or None.
    """

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
    """The model for a player's full build.

    Fields:
        - headgear (GearItem): The player's headgear.
        - clothing (GearItem): The player's clothing.
        - shoes (GearItem): The player's shoes.
    """

    headgear: GearItem
    clothing: GearItem
    shoes: GearItem


class Nameplate(BaseModel):
    """The model for a player's nameplate.

    Fields:
        - badges (BadgeType): The badges on the nameplate.
        - text_color (str): The text color of the nameplate. This is a hex
            string with the format #rrggbbaa.
        - background_id (str): The background ID of the nameplate.
    """

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
    """The model for a player.

    Fields:
        - name (str): The name the player has set for themselves.
        - npln_id (str): The NPLN ID of the player. This is a base64-decoded
            string from the player's ID.
        - me (bool): Whether or not the player is the user.
        - player_number (Optional[str]): The player discriminator. This is only
            not present during a player's first match. Can be 5 digits long,
            and can contain hex letters, but is usually 4 digits long and only
            contains numbers.
        - splashtag (str): The splashtag of the player.
        - nameplate (Nameplate): The nameplate of the player.
        - weapon_name (str): The name of the player's weapon.
        - weapon_id (int): The ID of the player's weapon.
        - sub_name (str): The name of the player's sub weapon.
        - special_name (str): The name of the player's special weapon.
        - inked (int): The amount of ink the player inked.
        - species (SpeciesType): The species of the player. This is either
            "inkling" or "octoling".
        - scoreboard_position (int): The position of the player on the
            scoreboard. This is 0-indexed.
        - gear (Gear): The gear of the player.
        - disconnected (bool): Whether or not the player disconnected.
        - kills_or_assists (Optional[int]): The amount of kills or assists the
            player got. Only present if the player did not disconnect.
        - assists (Optional[int]): The amount of assists the player got. Only
            present if the player did not disconnect.
        - kills (Optional[int]): The amount of kills the player got. Only
            present if the player did not disconnect.
        - deaths (Optional[int]): The amount of deaths the player got. Only
            present if the player did not disconnect.
        - specials (Optional[int]): The amount of specials the player got. Only
            present if the player did not disconnect.
        - signals (Optional[int]): The amount of signals the player got. Only
            present if the player did not disconnect, and only greater than 0
            in Tricolor matches.
        - crown (Optional[bool]): Whether or not the player has a crown. Only
            present in Xbattles and Splatfest matches.
        - crown_type (Optional[CrownType]): The type of crown the player has.
            Only present in splatfest matches.
    """

    name: str
    npln_id: str
    me: bool
    player_number: Optional[str] = None
    splashtag: str
    nameplate: Nameplate
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
    crown: Optional[bool] = None
    crown_type: Optional[CrownType] = None
