from typing import Optional

from pydantic import BaseModel


class XPower(BaseModel):
    lastXPower: float


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
