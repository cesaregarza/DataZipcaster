from pydantic import BaseModel

from data_zipcaster.models.splatnet.submodels.players import MaskingImage

__all__ = [
    "HistoryGroupOnlyFirst",
    "HGFGroupNodeItem",
    "HGFNodeItem",
    "HGFHistoryDetails",
    "HGFPlayer",
    "HGFWeapon",
    "HGFSpecialWeapon",
    "MaskingImage",
]


class HGFSpecialWeapon(BaseModel):
    maskingImage: MaskingImage
    id: str


class HGFWeapon(BaseModel):
    specialWeapon: HGFSpecialWeapon
    id: str


class HGFPlayer(BaseModel):
    weapon: HGFWeapon
    id: str


class HGFNodeItem(BaseModel):
    player: HGFPlayer
    id: str


class HGFHistoryDetails(BaseModel):
    nodes: list[HGFNodeItem]


class HGFGroupNodeItem(BaseModel):
    historyDetails: HGFHistoryDetails


class HistoryGroupOnlyFirst(BaseModel):
    nodes: list[HGFGroupNodeItem]
