from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.submodels.common import Color, Url
from data_zipcaster.models.splatnet.submodels.typing import (
    ResultType,
    SpeciesType,
    TricolorRoleType,
)


class Badge(BaseModel):
    image: Url
    id: str


class Background(BaseModel):
    textColor: Color
    image: Url
    id: str


class NamePlate(BaseModel):
    badges: list[Badge | None]
    background: Background


class MaskingImage(BaseModel):
    width: int
    height: int
    maskImageUrl: str
    overlayImageUrl: str


class SpecialWeapon(BaseModel):
    maskingImage: MaskingImage
    id: str
    name: str
    image: Url


class SubWeapon(BaseModel):
    name: str
    image: Url
    id: str


class Weapon(BaseModel):
    name: str
    image: Url
    specialWeapon: SpecialWeapon
    id: str
    image3d: Url
    image2d: Url
    image3dThumbnail: Url
    image2dThumbnail: Url
    subWeapon: SubWeapon


class GearPower(BaseModel):
    name: str
    image: Url


class UsualGearPower(BaseModel):
    name: str
    desc: str
    image: Url
    isEmptySlot: bool


class Brand(BaseModel):
    name: str
    image: Url
    id: str
    usualGearPower: UsualGearPower


class Gear(BaseModel):
    name: str
    thumbnailImage: Optional[Url] = None
    isGear: str
    primaryGearPower: GearPower
    additionalGearPowers: list[GearPower]
    originalImage: Url
    brand: Brand


class PlayerResult(BaseModel):
    kill: int
    death: int
    assist: int
    special: int
    noroshiTry: Optional[int] = None


class PlayerRoot(BaseModel):
    isPlayer: str
    byname: str
    name: str
    nameId: str
    nameplate: NamePlate
    id: str
    headGear: Gear
    clothingGear: Gear
    shoesGear: Gear
    paint: int


class Player(PlayerRoot):
    isMyself: bool
    weapon: Weapon
    species: SpeciesType
    result: Optional[PlayerResult] = None
    crown: bool
    festDragonCert: str


class TeamResult(BaseModel):
    paint_ratio: Optional[float] = None
    score: Optional[int] = None
    noroshi: Optional[int] = None


class Team(BaseModel):
    color: Color
    result: Optional[TeamResult] = None
    tricolorRole: Optional[TricolorRoleType] = None
    festTeamName: Optional[str] = None
    festUniformBonusRate: Optional[float] = None
    judgement: Optional[ResultType] = None
    players: list[Player]
    order: int
    festStreakWinCount: Optional[int] = None
    festUniformName: Optional[str] = None
