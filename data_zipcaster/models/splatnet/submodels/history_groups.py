from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.submodels.common import Url
from data_zipcaster.models.splatnet.submodels.mode_specific import (
    LeagueMatchEvent,
)
from data_zipcaster.models.splatnet.submodels.rules import (
    VsMode,
    VsRule,
    VsStage,
)
from data_zipcaster.models.splatnet.submodels.typing import (
    KnockoutType,
    ResultType,
)

__all__ = [
    "XMatchMeasurement",
    "BankaraMatchChallenge",
    "LeagueMatchHistoryGroup",
    "WeaponHistoryGroup",
    "PlayerHistoryGroup",
    "MyTeamResult",
    "MyTeam",
    "OneHistoryDetail",
    "HGBankaraMatch",
    "NodeItems",
    "HistoryDetails",
    "GroupNodeItems",
    "HistoryGroups",
]


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


class WeaponHistoryGroup(BaseModel):
    name: str
    image: Url
    id: str


class PlayerHistoryGroup(BaseModel):
    weapon: WeaponHistoryGroup
    id: str
    festGrade: Optional[str] = None


class MyTeamResult(BaseModel):
    paintPoint: Optional[int] = None
    score: Optional[int] = None


class MyTeam(BaseModel):
    result: Optional[MyTeamResult] = None


class OneHistoryDetail(BaseModel):
    id: str


class HGBankaraMatch(BaseModel):
    earnedUdemaePoint: Optional[int] = None


class NodeItems(BaseModel):
    id: str
    vsMode: VsMode
    vsRule: VsRule
    vsStage: VsStage
    judgement: ResultType
    player: PlayerHistoryGroup
    knockout: Optional[KnockoutType] = None
    myTeam: MyTeam
    nextHistoryDetail: Optional[OneHistoryDetail] = None
    previousHistoryDetail: Optional[OneHistoryDetail] = None
    udemae: Optional[str] = None
    bankaraMatch: Optional[HGBankaraMatch] = None
    playedTime: Optional[str] = None


class HistoryDetails(BaseModel):
    nodes: list[NodeItems]


class GroupNodeItems(BaseModel):
    xMatchMeasurement: Optional[XMatchMeasurement] = None
    historyDetails: HistoryDetails
    bankaraMatchChallenge: Optional[BankaraMatchChallenge] = None
    leagueMatchHistoryGroup: Optional[LeagueMatchHistoryGroup] = None


class HistoryGroups(BaseModel):
    nodes: list[GroupNodeItems]
