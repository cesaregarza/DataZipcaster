from typing import Literal

from typing_extensions import NotRequired, TypedDict

from data_zipcaster.schemas.overview import VsOverviewDict
from data_zipcaster.schemas.players import PlayerDict
from data_zipcaster.schemas.typing import (
    KnockoutType,
    ModeType,
    ResultType,
    RuleType,
)


class MedalDict(TypedDict):
    name: str
    rank: Literal["GOLD", "SILVER"]


class TeamResult(TypedDict):
    paint_ratio: float | None
    score: int | None
    noroshi: int | None
    team_result: ResultType


class SplatfestTeamDict(TypedDict):
    team_name: str
    synergy_bonus: NotRequired[float]
    synergy_name: NotRequired[str]
    tricolor_role: NotRequired[Literal["defense", "attack1", "attack2"]]


class TeamDict(TypedDict):
    players: list[PlayerDict]
    color: str
    order: int
    result: NotRequired[TeamResult]
    splatfest: NotRequired[SplatfestTeamDict]


class SplatfestMetadataDict(TypedDict):
    match_multiplier: int
    clout: int
    jewel: int


class VsExtractDict(TypedDict):
    knockout: KnockoutType
    mode: ModeType
    result: ResultType
    rule: RuleType
    stage: str
    start_time: float
    duration: int
    teams: list[TeamDict]
    medals: list[MedalDict]
    id: str
    series_metadata: NotRequired[VsOverviewDict]
    match_power: NotRequired[float]
    challenge_id: NotRequired[str]
    splatfest_metadata: NotRequired[SplatfestMetadataDict]
