from typing import Optional

from pydantic import BaseModel, validator

from data_zipcaster.constants import RANKS

__all__ = [
    "AnarchyMetadata",
    "AnarchySeriesMetadata",
    "AnarchyOpenMetadata",
    "XMetadata",
]


class AnarchyMetadata(BaseModel):
    """The model for metadata in an Anarchy match.

    Fields:
        - rank_before (str): The rank before the match.
        - rank_after (str): The rank after the match.
        - rank_before_s_plus (Optional[int]): The S+ rank before the match. Only
            used if the rank is S+.
        - rank_after_s_plus (Optional[int]): The S+ rank after the match. Only
            used if the rank is S+.
        - rank_exp_change (Optional[int]): The change in rank experience points
            after the match. Not present in the middle of a series.
        - is_rank_up (Optional[bool]): Whether the series was a rank up series.
            Does not indicate the player ranked up after the match.
    """

    rank_before: str
    rank_after: str
    rank_before_s_plus: Optional[int] = None
    rank_after_s_plus: Optional[int] = None
    rank_exp_change: Optional[int] = None
    is_rank_up: Optional[bool] = None

    @validator("rank_before", "rank_after")
    def validate_rank(cls, v: str) -> str:
        if v.upper() not in RANKS:
            raise ValueError(f"{v} is not a valid rank")
        return v

    @validator("rank_before_s_plus", "rank_after_s_plus")
    def validate_rank_s_plus(cls, v: int) -> int:
        if v < 0 or v > 50:
            raise ValueError(f"{v} is not a valid rank")
        return v


class AnarchySeriesMetadata(AnarchyMetadata):
    """The model for metadata in an Anarchy series. Contains all fields from
    AnarchyMetadata and adds series win/loss counts.

    Fields:
        - rank_before (str): The rank before the match.
        - rank_after (str): The rank after the match.
        - rank_before_s_plus (Optional[int]): The S+ rank before the match. Only
            used if the rank is S+.
        - rank_after_s_plus (Optional[int]): The S+ rank after the match. Only
            used if the rank is S+.
        - rank_exp_change (Optional[int]): The change in rank experience points
            after the match. Not present in the middle of a series.
        - is_rank_up (Optional[bool]): Whether the series was a rank up series.
            Does not indicate the player ranked up after the match.
        - series_win_count (int): The number of wins in the series so far.
        - series_lose_count (int): The number of losses in the series so far.
    """

    series_win_count: int
    series_lose_count: int


class AnarchyOpenMetadata(AnarchyMetadata):
    """The model for metadata in an Anarchy match.

    Fields:
        - rank_before (str): The rank before the match.
        - rank_after (str): The rank after the match.
        - rank_before_s_plus (Optional[int]): The S+ rank before the match. Only
            used if the rank is S+.
        - rank_after_s_plus (Optional[int]): The S+ rank after the match. Only
            used if the rank is S+.
        - rank_exp_change (Optional[int]): The change in rank experience points
            after the match. Not present in the middle of a series.
        - is_rank_up (Optional[bool]): Whether the series was a rank up series.
            Does not indicate the player ranked up after the match.
    """

    pass


class XMetadata(BaseModel):
    """The model for metadata in an Xbattles match.

    Fields:
        - x_power_after (Optional[float]): The X Power after the match. Only
            present in the last match of a series.
        - rank_estimate (Optional[int]): The estimated rank after the match.
            Only present for Top 3000 players.
        - series_win_count (int): The number of wins in the series so far.
        - series_lose_count (int): The number of losses in the series so far.
    """

    x_power_after: Optional[float] = None
    rank_estimate: Optional[int] = None
    series_win_count: int
    series_lose_count: int
