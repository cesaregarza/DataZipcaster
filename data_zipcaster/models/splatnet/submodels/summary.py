from typing import Optional

from pydantic import BaseModel

__all__ = [
    "XPower",
    "Summary",
]


class XPower(BaseModel):
    lastXPower: Optional[float] = None


class Summary(BaseModel):
    assistAverage: float
    deathAverage: float
    killAverage: float
    perUnitTimeMinute: int
    specialAverage: float
    xPowerAr: Optional[XPower] = None
    xPowerCl: Optional[XPower] = None
    xPowerGl: Optional[XPower] = None
    xPowerLf: Optional[XPower] = None
    win: int
    lose: int
