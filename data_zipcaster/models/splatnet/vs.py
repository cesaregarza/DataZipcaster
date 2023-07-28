from typing import Optional

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

__all__ = [
    "Award",
    "VsHistoryDetail",
    "VsDetail",
    "MetadataHistories",
    "AnarchyMetadata",
    "XMetadata",
    "TurfMetadata",
    "ChallengeMetadata",
]


class Award(BaseModel):
    """This is the award model.

    Fields:
        - name (str) - The name of the award.
        - rank (AwardRankType) - The rank of the award. "GOLD" or "SILVER".
    """

    name: str
    rank: AwardRankType


class VsHistoryDetail(BaseModel):
    """This is the actual history detail model.

    Fields:
        - typename (str) - Not sure what this is.
        - id (str) - The match's id. Base64 encoded.
        - vsRule (VsRule) - The rule of the match.
        - vsMode (VsMode) - The mode of the match.
        - player (PlayerRoot) - The player's data. Has less data than the player
            model in myTeam.
        - judgement (ResultType) - The result of the match.
        - myTeam (Team) - The player's team.
        - vsStage (VsStage) - The stage of the match.
        - festMatch (Optional[SplatfestMatch]) - The splatfest match data.
        - knockout (Optional[KnockoutType]) - The knockout type of the match.
        - otherTeams (list[Team]) - The other teams in the match.
        - bankaraMatch (Optional[BankaraMatch]) - The Anarchy match data.
        - leagueMatch (Optional[LeagueMatch]) - The Challenge match data.
        - xMatch (Optional[XMatch]) - The Xbattle match data.
        - duration (int) - The duration of the match in seconds.
        - playedTime (str) - The time the match was played.
        - awards (list[Award]) - The awards the player got.
        - nextHistoryDetail (Optional[OneHistoryDetail]) - The next match's
            ID. Base64 encoded.
        - previousHistoryDetail (Optional[OneHistoryDetail]) - The previous
            match's ID. Base64 encoded.
    """

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
    """This is the root model for the vs history detail. A thin wrapper around
    the actual history detail.

    Fields:
        - vsHistoryDetail (VsHistoryDetail) - The actual history detail.
    """

    vsHistoryDetail: VsHistoryDetail


class MetadataHistories(BaseModel):
    """This is the metadata histories model.

    Fields:
        - summary (Summary) - The summary of the metadata.
        - historyGroups (HistoryGroups) - The history groups of the metadata.
        - historyGroupOnlyFirst (Optional[HistoryGroupOnlyFirst]) - Not sure
            what this is.
    """

    summary: Summary
    historyGroups: HistoryGroups
    historyGroupOnlyFirst: Optional[HistoryGroupOnlyFirst] = None


class AnarchyMetadata(BaseModel):
    """This is the Anarchy metadata model.

    Fields:
        - bankaraBattleHistories (MetadataHistories) - The bankara battle
            histories.
    """

    bankaraBattleHistories: MetadataHistories


class XMetadata(BaseModel):
    """This is the Xbattle metadata model.

    Fields:
        - xBattleHistories (MetadataHistories) - The Xbattle histories.
    """

    xBattleHistories: MetadataHistories


class TurfMetadata(BaseModel):
    """This is the turf war metadata model.

    Fields:
        - regularBattleHistories (MetadataHistories) - The turf war histories.
    """

    regularBattleHistories: MetadataHistories


class ChallengeMetadata(BaseModel):
    """This is the challenge metadata model.

    Fields:
        - eventBattleHistories (MetadataHistories) - The challenge histories.
    """

    eventBattleHistories: MetadataHistories
