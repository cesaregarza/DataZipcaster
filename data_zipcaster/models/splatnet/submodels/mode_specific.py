from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.submodels.typing import MatchMultiplierType

__all__ = [
    "SplatfestMatch",
    "BankaraMatch",
    "LeagueMatch",
    "LeagueMatchEvent",
    "XMatch",
]


class SplatfestMatch(BaseModel):
    dragonMatchType: MatchMultiplierType
    contribution: int
    jewel: int
    myFestPower: Optional[float] = None


class BankaraPower(BaseModel):
    power: float


class BankaraMatch(BaseModel):
    earnedUdemaePoint: Optional[int] = None
    mode: str
    bankaraPower: Optional[BankaraPower | float] = None


class LeagueMatchEvent(BaseModel):
    name: str
    id: str


class LeagueMatch(BaseModel):
    leagueMatchEvent: LeagueMatchEvent
    myLeaguePower: Optional[float] = None


class XMatch(BaseModel):
    lastXPower: Optional[float] = None
