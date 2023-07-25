from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.player import MaskingImage


class SpecialWeapon(BaseModel):
    maskingImage: MaskingImage
    id: str


class Weapon(BaseModel):
    specialWeapon: SpecialWeapon
    id: str


class Player(BaseModel):
    weapon: Weapon
    id: str


class NodeItem(BaseModel):
    player: Player
    id: str


class HistoryDetails(BaseModel):
    nodes: list[NodeItem]


class GroupNodeItem(BaseModel):
    historyDetails: HistoryDetails


class HistoryGroupOnlyFirst(BaseModel):
    nodes: list[GroupNodeItem]
