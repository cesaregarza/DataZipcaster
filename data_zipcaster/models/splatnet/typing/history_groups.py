from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.common import Url
from data_zipcaster.models.splatnet.typing.mode_specific import LeagueMatchEvent
from data_zipcaster.models.splatnet.typing.rules import VsMode, VsRule, VsStage


class XMatchMeasurement(BaseModel):
    state: str
    xPowerAfter: Optional[float] = None
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
    isUdemaeUp: Optional[bool] = None
    udemaeAfter: Optional[str] = None
    earnedUdemaePoint: Optional[int] = None


class LeagueMatchHistoryGroup(BaseModel):
    leagueMatchEvent: LeagueMatchEvent
    vsRule: VsRule
    teamComposition: str
    myLeaguePower: Optional[float] = None


class Weapon(BaseModel):
    name: str
    image: Url
    id: str


class Player(BaseModel):
    weapon: Weapon
    id: str
    festGrade: Optional[str] = None


class MyTeamResult(BaseModel):
    paintPoint: Optional[int] = None
    score: Optional[int] = None


class MyTeam(BaseModel):
    result: Optional[MyTeamResult] = None


class OneHistoryDetail(BaseModel):
    id: str


class BankaraMatch(BaseModel):
    earnedUdemaePoint: Optional[int] = None


class NodeItems(BaseModel):
    id: str
    vsMode: VsMode
    vsRule: VsRule
    vsStage: VsStage
    judgement: str
    player: Player
    knockout: Optional[str] = None
    myTeam: MyTeam
    nextHistoryDetail: Optional[OneHistoryDetail] = None
    previousHistoryDetail: Optional[OneHistoryDetail] = None
    udemae: Optional[str] = None
    bankaraMatch: Optional[BankaraMatch] = None
    playedTime: Optional[str] = None


class HistoryDetails(BaseModel):
    nodes: list[NodeItems]


class GroupNodeItems(BaseModel):
    XMatchMeasurement: Optional[XMatchMeasurement] = None
    historyDetails: HistoryDetails
    bankaraMatchChallenge: Optional[BankaraMatchChallenge] = None
    leagueMatchHistoryGroup: Optional[LeagueMatchHistoryGroup] = None


class HistoryGroups(BaseModel):
    nodes: list[GroupNodeItems]
