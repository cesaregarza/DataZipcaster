from typing import TypeAlias

from typing_extensions import NotRequired, TypedDict


class AnarchySeriesOverviewDict(TypedDict):
    rank_before: str
    rank_after: str
    rank_before_s_plus: NotRequired[int]
    rank_after_s_plus: NotRequired[int]
    rank_exp_change: NotRequired[int]
    is_rank_up: NotRequired[bool]
    series_win_count: int
    series_lose_count: int


class AnarchyOpenOverviewDict(TypedDict):
    rank_before: str
    rank_after: str
    rank_before_s_plus: NotRequired[int]
    rank_after_s_plus: NotRequired[int]
    rank_exp_change: int


class XOverviewDict(TypedDict):
    x_power_after: NotRequired[float]
    rank_estimate: int
    series_win_count: int
    series_lose_count: int


AnarchyOverviewDict: TypeAlias = (
    AnarchySeriesOverviewDict | AnarchyOpenOverviewDict
)
AnarchySeriesOverviewOut: TypeAlias = dict[str, AnarchySeriesOverviewDict]
AnarchyOpenOverviewOut: TypeAlias = dict[str, AnarchyOpenOverviewDict]
AnarchyOverviewOut: TypeAlias = (
    AnarchySeriesOverviewOut | AnarchyOpenOverviewOut
)
VsOverviewDict: TypeAlias = AnarchyOverviewDict | XOverviewDict
VsOverviewOut: TypeAlias = (
    AnarchyOverviewOut
    | dict[str, XOverviewDict]
    | dict[str, AnarchyOverviewDict]
)
