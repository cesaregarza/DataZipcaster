from typing import Callable, TypeAlias

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.vs_battles import (
    build_vs_extract,
    extract_anarchy,
    extract_xbattle,
)
from data_zipcaster.schemas.vs_modes import VsExtractDict

Extract_Functions: TypeAlias = (
    Callable[[list[QueryResponse], QueryResponse], list[VsExtractDict]]
    | Callable[[list[QueryResponse], QueryResponse | None], list[VsExtractDict]]
)

EXTRACT_MAP: dict[str, Extract_Functions] = {
    "xbattle": extract_xbattle,
    "anarchy": extract_anarchy,
    "turf": build_vs_extract,
    "private": build_vs_extract,
    "challenge": build_vs_extract,
}
