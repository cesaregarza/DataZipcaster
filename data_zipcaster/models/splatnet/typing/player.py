from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.common import Color, Url


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
    thumbnailImage: Url
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
    noroshiTry: int | None = None


class PlayerRoot(BaseModel):
    isPlayer: str
    byname: str
    name: str
    nameId: str
    nameplate: NamePlate
    id: str
    headGear: Gear
    clothesGear: Gear
    shoesGear: Gear
    paint: int


class Player(PlayerRoot):
    isMyself: bool
    weapon: Weapon
    species: str
    result: PlayerResult | None = None
    crown: bool
    festDragonCert: str


class TeamResult(BaseModel):
    paint_ratio: float | None = None
    score: int | None = None
    noroshi: int | None = None


class Team(BaseModel):
    color: Color
    result: TeamResult | None = None
    tricolorRole: str | None = None
    festTeamName: str | None = None
    festUniformBonusRate: float | None = None
    judgement: str | None = None
    players: list[Player]
    order: int
    festStreakWinCount: int | None = None
    festUniformName: str | None = None
