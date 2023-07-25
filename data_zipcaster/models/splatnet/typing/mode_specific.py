from typing import Optional

from pydantic import BaseModel


class SplatfestMatch(BaseModel):
    dragonMatchType: str
    contribution: int
    jewel: int
    myFestPower: Optional[float] = None


class BankaraMatch(BaseModel):
    earnedUdemaePoint: Optional[int] = None
    mode: str
    bankaraPower: Optional[float] = None


class LeagueMatchEvent(BaseModel):
    name: str
    id: str


class LeagueMatch(BaseModel):
    leagueMatchEvent: LeagueMatchEvent
    myLeaguePower: Optional[float] = None


class XMatch(BaseModel):
    lastXPower: Optional[float] = None
