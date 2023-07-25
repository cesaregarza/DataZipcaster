from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.history_groups import HistoryGroups
from data_zipcaster.models.splatnet.typing.history_groups_first import (
    HistoryGroupOnlyFirst,
)
from data_zipcaster.models.splatnet.typing.mode_specific import (
    BankaraMatch,
    LeagueMatch,
    SplatfestMatch,
    XMatch,
)
from data_zipcaster.models.splatnet.typing.player import PlayerRoot, Team
from data_zipcaster.models.splatnet.typing.rules import VsMode, VsRule, VsStage
from data_zipcaster.models.splatnet.typing.summary import Summary


class Award(BaseModel):
    name: str
    rank: str


class VsHistoryDetail(BaseModel):
    typename: str
    id: str
    vsRule: VsRule
    vsMode: VsMode
    player: PlayerRoot
    judgement: str
    myTeam: Team
    vsStage: VsStage
    festMatch: SplatfestMatch
    knockout: str | None = None
    otherTeams: list[Team]
    bankaraMatch: BankaraMatch
    leagueMatch: LeagueMatch
    xMatch: XMatch
    duration: int
    playedTime: str
    awards: list[Award]
    nextHistoryDetail: str | None = None
    previousHistoryDetail: str | None = None


class VsDetail(BaseModel):
    vsHistoryDetail: VsHistoryDetail


class MetaData(BaseModel):
    summary: Summary
    historyGroups: HistoryGroups
    historyGroupOnlyFirst: HistoryGroupOnlyFirst
