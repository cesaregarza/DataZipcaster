from typing import TypeAlias

from data_zipcaster.models.main.metadata import (
    AnarchyOpenMetadata,
    AnarchySeriesMetadata,
)

AnarchyMetadata: TypeAlias = AnarchyOpenMetadata | AnarchySeriesMetadata
