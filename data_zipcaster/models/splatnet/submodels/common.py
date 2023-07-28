from pydantic import BaseModel

__all__ = [
    "Url",
    "Color",
]


class Url(BaseModel):
    url: str


class Color(BaseModel):
    a: float
    b: float
    g: float
    r: float
