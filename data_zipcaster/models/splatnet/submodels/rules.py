from typing import Optional

from pydantic import BaseModel

from data_zipcaster.models.splatnet.submodels.common import Url
from data_zipcaster.models.splatnet.submodels.typing import RuleType

__all__ = [
    "VsRule",
    "VsMode",
    "VsStage",
]


class VsRule(BaseModel):
    name: str
    id: str
    rule: Optional[RuleType] = None


class VsMode(BaseModel):
    mode: str
    id: str


class VsStage(BaseModel):
    name: str
    image: Url
    id: str
