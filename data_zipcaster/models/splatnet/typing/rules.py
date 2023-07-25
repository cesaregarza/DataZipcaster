from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.common import Url


class VsRule(BaseModel):
    name: str
    id: str
    rule: Optional[str] = None


class VsMode(BaseModel):
    mode: str
    id: str


class VsStage(BaseModel):
    name: str
    image: Url
    id: str
