from pydantic import BaseModel


class XPower(BaseModel):
    lastXPower: float


class Summary(BaseModel):
    assistAverage: float
    deathAverage: float
    killAverage: float
    perUnitTimeMinute: int
    specialAverage: float
    xPowerAr: XPower
    xPowerCl: XPower
    xPowerGl: XPower
    xPowerLf: XPower
    win: int
    lose: int
