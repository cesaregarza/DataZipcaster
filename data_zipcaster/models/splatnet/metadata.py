from pydantic import BaseModel

from data_zipcaster.models.splatnet.typing.history_groups import HistoryGroups
from data_zipcaster.models.splatnet.typing.history_groups_first import (
    HistoryGroupOnlyFirst,
)
from data_zipcaster.models.splatnet.typing.summary import Summary


class MetaData(BaseModel):
    summary: Summary
    historyGroups: HistoryGroups
    historyGroupOnlyFirst: HistoryGroupOnlyFirst
