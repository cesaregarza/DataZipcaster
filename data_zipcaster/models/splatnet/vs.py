from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.history_groups import (
    HistoryGroups,
    OneHistoryDetail,
)
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
from data_zipcaster.models.utils import strip_prefix_keys


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
    festMatch: Optional[SplatfestMatch] = None
    knockout: Optional[str] = None
    otherTeams: list[Team]
    bankaraMatch: Optional[BankaraMatch] = None
    leagueMatch: Optional[LeagueMatch] = None
    xMatch: Optional[XMatch] = None
    duration: int
    playedTime: str
    awards: list[Award]
    nextHistoryDetail: Optional[OneHistoryDetail] = None
    previousHistoryDetail: Optional[OneHistoryDetail] = None


class VsDetail(BaseModel):
    vsHistoryDetail: VsHistoryDetail


class MetadataHistories(BaseModel):
    summary: Summary
    historyGroups: HistoryGroups
    historyGroupOnlyFirst: Optional[HistoryGroupOnlyFirst] = None


class AnarchyMetadata(BaseModel):
    bankaraBattleHistories: MetadataHistories


class XMetadata(BaseModel):
    xBattleHistories: MetadataHistories


class TurfMetadata(BaseModel):
    regularBattleHistories: MetadataHistories


class ChallengeMetadata(BaseModel):
    eventBattleHistories: MetadataHistories
