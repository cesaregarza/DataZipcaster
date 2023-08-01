import datetime as dt
from typing import Optional

from pydantic import BaseModel, validator

from data_zipcaster.models.main.metadata import AnarchyMetadata, XMetadata
from data_zipcaster.models.main.players import Player
from data_zipcaster.models.main.typing import (
    AwardRankType,
    KnockoutType,
    ModeType,
    ResultType,
    RuleType,
    TricolorRoleType,
)

__all__ = [
    "Awards",
    "TeamResult",
    "SplatfestTeam",
    "Team",
    "SplatfestMetadata",
    "VsExtract",
]


class Awards(BaseModel):
    """The model for awards in a vs mode match.

    Fields:
        - name (str): The name of the award.
        - rank (AwardRankType): The rank of the award. Either "gold" or "silver"
    """

    name: str
    rank: AwardRankType


class TeamResult(BaseModel):
    """The result of a team in a vs mode match.

    Fields:
        - paint_ratio (Optional[float]): The paint ratio of the team.
        - score (Optional[int]): The score of the team.
        - noroshi (Optional[int]): How many Signals the team obtained. Only used
            during Splatfest.
        - team_result (ResultType): The result of the team, known as the
            judgement.
    """

    paint_ratio: Optional[float] = None
    score: Optional[int] = None
    noroshi: Optional[int] = None
    team_result: ResultType


class SplatfestTeam(BaseModel):
    """The Splatfest team data of a team in a vs mode match.

    Fields:
        - team_name (str): The name of the team.
        - synergy_bonus (Optional[float]): The synergy bonus value from the
            team's gear synergy.
        - synergy_name (Optional[str]): The name of the gear synergies the team
            has.
        - tricolor_role (Optional[TricolorRoleType]): The tricolor role of the
            team.
    """

    team_name: str
    synergy_bonus: Optional[float] = None
    synergy_name: Optional[str] = None
    tricolor_role: TricolorRoleType | None = None


class Team(BaseModel):
    """The data of a team in a vs mode match.

    Fields:
        - players (list[Player]): The players in the team.
        - color (str): The color of the team. A hex color code, prepended by a
            "#".
        - order (int): The order of the team, 1-indexed.
        - result (Optional[TeamResult]): The result of the team.
        - splatfest (Optional[SplatfestTeam]): The Splatfest team data of the
            team.
    """

    players: list[Player]
    color: str
    order: int
    result: Optional[TeamResult] = None
    splatfest: Optional[SplatfestTeam] = None


class SplatfestMetadata(BaseModel):
    """The metadata of a Splatfest match.

    Fields:
        - match_multiplier (int): The match multiplier of the Splatfest match.
        - clout (int): The clout earned in the Splatfest match.
        - jewel (int): Not sure what this is, but it's in the data.
    """

    match_multiplier: int
    clout: int
    jewel: int


class VsExtract(BaseModel):
    """The main model for vs mode matches.

    Fields:
        - knockout (KnockoutType): The knockout status of the match.
        - mode (ModeType): The mode of the match.
        - result (ResultType): The result of the match.
        - rule (RuleType): The rule of the match.
        - stage (str): The stage of the match. Is the stage's ID, everything
            after "VsStage-" in the base64-decoded stage ID.
        - start_time (dt.datetime): The start time of the match.
        - duration (dt.timedelta): The duration of the match.
        - teams (list[Team]): The teams of the match.
        - awards (list[Awards]): The awards of the match.
        - id (str): The ID of the match. Is the base64-encoded battle ID.
        - series_metadata (Optional[AnarchyMetadata | XMetadata]): The metadata
            of the series, if the match is part of a series.
        - match_power (Optional[float]): The match power of the match, if the
            match is part of a series.
        - challenge_id (Optional[str]): The challenge ID of the match, if the
            match is part of a challenge.
        - splatfest_metadata (Optional[SplatfestMetadata]): The metadata of the
            Splatfest, if the match is part of a Splatfest.
    """

    knockout: KnockoutType
    mode: ModeType
    result: ResultType
    rule: RuleType
    stage: str
    start_time: dt.datetime
    duration: dt.timedelta
    teams: list[Team]
    awards: list[Awards]
    id: str
    series_metadata: Optional[AnarchyMetadata | XMetadata] = None
    match_power: Optional[float] = None
    challenge_id: Optional[str] = None
    splatfest_metadata: Optional[SplatfestMetadata] = None

    @validator("teams")
    def validate_teams(cls, v):
        if len(v) < 2:
            raise ValueError("teams must have at least 2 elements")
        return v
