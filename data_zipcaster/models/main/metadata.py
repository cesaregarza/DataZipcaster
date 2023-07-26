from typing import Optional

from pydantic import BaseModel, validator

from data_zipcaster.constants import RANKS


class AnarchyMetadata(BaseModel):
    rank_before: str
    rank_after: str
    rank_before_s_plus: Optional[int] = None
    rank_after_s_plus: Optional[int] = None
    rank_exp_change: int
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
    series_win_count: int
    series_lose_count: int


class AnarchyOpenMetadata(AnarchyMetadata):
    pass


class XMetadata(BaseModel):
    x_power_after: Optional[float] = None
    rank_estimate: Optional[int] = None
    series_win_count: int
    series_lose_count: int
