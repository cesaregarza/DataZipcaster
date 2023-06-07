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


class TeamDict(TypedDict):
    players: list[PlayerDict]
    color: str
    result: NotRequired[TeamResult]


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
