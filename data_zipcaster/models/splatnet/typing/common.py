from pydantic import BaseModel


class Url(BaseModel):
    url: str


class Color(BaseModel):
    a: float
    b: float
    g: float
    r: float
