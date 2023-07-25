from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.common import Url
from data_zipcaster.models.splatnet.typing.mode_specific import LeagueMatchEvent
from data_zipcaster.models.splatnet.typing.rules import VsMode, VsRule, VsStage


class XMatchMeasurement(BaseModel):
    state: str
    xPowerAfter: float | None = None
    isInitial: bool
    winCount: int
    loseCount: int
    maxInitialBattleCount: int
    maxWinCount: int
    maxLoseCount: int
    vsRule: VsRule


class BankaraMatchChallenge(BaseModel):
    winCount: int
    loseCount: int
    maxWinCount: int
    maxLoseCount: int
    state: str
    isPromo: bool
    isUdemaeUp: bool | None = None
    udemaeAfter: str | None = None
    earnedUdemaePoint: int | None = None


class LeagueMatchHistoryGroup(BaseModel):
    leagueMatchEvent: LeagueMatchEvent
    vsRule: VsRule
    teamComposition: str
    myLeaguePower: float | None = None


class Weapon(BaseModel):
    name: str
    image: Url
    id: str


class Player(BaseModel):
    weapon: Weapon
    id: str
    festGrade: str | None = None


class MyTeamResult(BaseModel):
    paintPoint: int | None = None
    score: int | None = None


class MyTeam(BaseModel):
    result: list[MyTeamResult] | None = None


class OneHistoryDetail(BaseModel):
    id: str


class BankaraMatch(BaseModel):
    earnedUdemaePoint: int | None = None


class NodeItems(BaseModel):
    id: str
    vsMode: VsMode
    vsRule: VsRule
    vsStage: VsStage
    judgement: str
    player: Player
    knockout: str | None = None
    myTeam: MyTeam
    nextHistoryDetail: OneHistoryDetail | None = None
    previousHistoryDetail: OneHistoryDetail | None = None
    udemae: str | None = None
    bankaraMatch: BankaraMatch | None = None
    playedTime: str | None = None


class HistoryDetails(BaseModel):
    nodes: list[NodeItems]


class GroupNodeItems(BaseModel):
    XMatchMeasurement: XMatchMeasurement | None = None
    historyDetails: HistoryDetails
    bankaraMatchChallenge: BankaraMatchChallenge | None = None
    leagueMatchHistoryGroup: LeagueMatchHistoryGroup | None = None


class HistoryGroups(BaseModel):
    nodes: list[GroupNodeItems]
