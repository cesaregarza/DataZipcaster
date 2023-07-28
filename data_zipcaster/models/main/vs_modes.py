import datetime as dt
from typing import Literal, Optional

from pydantic import BaseModel, validator

from data_zipcaster.models.main.metadata import AnarchySeriesMetadata, XMetadata
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
    name: str
    rank: AwardRankType


class TeamResult(BaseModel):
    paint_ratio: Optional[float] = None
    score: Optional[int] = None
    noroshi: Optional[int] = None
    team_result: ResultType


class SplatfestTeam(BaseModel):
    team_name: str
    synergy_bonus: Optional[float] = None
    synergy_name: Optional[str] = None
    tricolor_role: TricolorRoleType | None = None


class Team(BaseModel):
    players: list[Player]
    color: str
    order: int
    result: Optional[TeamResult] = None
    splatfest: Optional[SplatfestTeam] = None


class SplatfestMetadata(BaseModel):
    match_multiplier: int
    clout: int
    jewel: int


class VsExtract(BaseModel):
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
    series_metadata: Optional[AnarchySeriesMetadata | XMetadata] = None

    @validator("teams")
    def validate_teams(cls, v):
        if len(v) <= 2:
            raise ValueError("teams must have at least 2 elements")
        return v
