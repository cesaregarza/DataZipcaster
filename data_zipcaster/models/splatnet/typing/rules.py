from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.common import Url


class vsRule(BaseModel):
    name: str
    id: str
    rule: str


class vsMode(BaseModel):
    mode: str
    id: str


class vsStage(BaseModel):
    name: str
    image: Url
    id: str
