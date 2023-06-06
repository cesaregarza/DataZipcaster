from typing import Literal

from typing_extensions import NotRequired, TypedDict

from data_zipcaster.importers.splatnet.types.aliases import (
    KnockoutType,
    ModeType,
    ResultType,
    RuleType,
)
from data_zipcaster.importers.splatnet.types.players import PlayerDict


class MedalDict(TypedDict):
    name: str
    rank: Literal["GOLD", "SILVER"]


class TeamResult(TypedDict):
    paint_ratio: float | None
    score: int | None
    noroshi: int | None


class TeamDict(TypedDict):
    team_players: list[PlayerDict]
    team_color: str
    team_result: NotRequired[TeamResult]


class VsExtractDict(TypedDict):
    knockout: KnockoutType
    mode: ModeType
    result: ResultType
    rule: RuleType
    stage: str
    start_time: float
    duration: int
    our_team: TeamDict
    their_team: TeamDict
    third_team: NotRequired[TeamDict]
    medals: list[MedalDict]
    id: str
