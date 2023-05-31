from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.common import (
    extract_duration,
    extract_id,
    extract_knockout,
    extract_medals,
    extract_mode,
    extract_result,
    extract_rule,
    extract_stage,
    extract_start_time,
    extract_team_data,
)
from data_zipcaster.importers.splatnet.extractors.overview import (
    extract_overview_xbattle,
)
from data_zipcaster.importers.splatnet.paths import vs_modes_paths


def extract_xbattle(
    overview: QueryResponse, detailed_battles: list[QueryResponse]
) -> list[dict]:
    out = []
    overview_data = extract_overview_xbattle(overview)
