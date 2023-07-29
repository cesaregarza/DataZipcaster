from pydantic import BaseModel

__all__ = [
    "Url",
    "Color",
]


class Url(BaseModel):
    """Generic URL model. Used for images.

    Fields:
        - url (str) - The URL.
    """

    url: str


class Color(BaseModel):
    """Generic color model. Used for colors.

    Fields:
        - a (float) - The alpha value.
        - b (float) - The blue value.
        - g (float) - The green value.
        - r (float) - The red value.
    """

    a: float
    b: float
    g: float
    r: float
