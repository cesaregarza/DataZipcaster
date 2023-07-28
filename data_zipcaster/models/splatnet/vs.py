from typing import Literal, Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.submodels import (
    AwardRankType,
    BankaraMatch,
    HistoryGroupOnlyFirst,
    HistoryGroups,
    KnockoutType,
    LeagueMatch,
    OneHistoryDetail,
    PlayerRoot,
    ResultType,
    SplatfestMatch,
    Summary,
    Team,
    VsMode,
    VsRule,
    VsStage,
    XMatch,
)


class Award(BaseModel):
    name: str
    rank: AwardRankType


class VsHistoryDetail(BaseModel):
    typename: str
    id: str
    vsRule: VsRule
    vsMode: VsMode
    player: PlayerRoot
    judgement: ResultType
    myTeam: Team
    vsStage: VsStage
    festMatch: Optional[SplatfestMatch] = None
    knockout: Optional[KnockoutType] = None
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
