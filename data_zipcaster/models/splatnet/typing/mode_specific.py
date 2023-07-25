from pydantic import BaseModel


class SplatfestMatch(BaseModel):
    dragonMatchType: str
    contribution: int
    jewel: int
    myFestPower: float | None = None


class BankaraMatch(BaseModel):
    earnedUdemaePoint: int | None = None
    mode: str
    bankaraPower: float | None = None


class LeagueMatchEvent(BaseModel):
    name: str
    id: str


class LeagueMatch(BaseModel):
    leagueMatchEvent: LeagueMatchEvent
    myLeaguePower: float | None = None


class XMatch(BaseModel):
    lastXPower: float | None = None
