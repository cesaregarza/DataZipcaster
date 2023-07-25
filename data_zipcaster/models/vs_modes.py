from typing import Literal

from pydantic import BaseModel, validator

from data_zipcaster.models.typing import (
    KnockoutType,
    ModeType,
    ResultType,
    RuleType,
)


class Medals(BaseModel):
    name: str
    rank: Literal["GOLD", "SILVER"]


class TeamResult(BaseModel):
    paint_ratio: float | None
    score: int | None
    noroshi: int | None
    team_result: ResultType


class SplatfestTeam(BaseModel):
    team_name: str
    synergy_bonus: float | None = None
    synergy_name: str | None = None
    tricolor_role: Literal["defense", "attack1", "attack2"] | None = None


class TeamDict(BaseModel):
    players: list[dict]
    color: str
    order: int
    result: TeamResult | None = None
    splatfest: SplatfestTeam | None = None


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
    start_time: float
    duration: int
    teams: list[TeamDict]
    medals: list[Medals]
    id: str
    series_metadata: dict | None = None

    @validator("teams")
    def validate_teams(cls, v):
        if len(v) <= 2:
            raise ValueError("teams must have at least 2 elements")
        return v

    @validator("medals")
    def validate_medals(cls, v):
        if len(v) != 3:
            raise ValueError("medals must have 3 elements")
        return v
