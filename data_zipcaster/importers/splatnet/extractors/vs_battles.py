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
    extract_overview_anarchy,
    extract_overview_xbattle,
)
from data_zipcaster.schemas.overview import VsOverviewOut
from data_zipcaster.schemas.vs_modes import VsExtractDict


def build_vs_extract(
    detailed_battles: list[QueryResponse],
    overview_data: VsOverviewOut | None = None,
) -> list[VsExtractDict]:
    out = []
    for battle in detailed_battles:
        knockout = extract_knockout(battle)
        mode = extract_mode(battle)
        result = extract_result(battle)
        rule = extract_rule(battle)
        stage = extract_stage(battle)
        start_time = extract_start_time(battle)
        team_data = extract_team_data(battle)
        duration = extract_duration(battle)
        medals = extract_medals(battle)
        battle_id = extract_id(battle)
        subout = VsExtractDict(
            knockout=knockout,
            mode=mode,
            result=result,
            rule=rule,
            stage=stage,
            start_time=start_time,
            teams=team_data,
            duration=duration,
            medals=medals,
            id=battle_id,
        )

        if (overview_data is not None) and (battle_id in overview_data):
            subout["series_metadata"] = overview_data[battle_id]
        out.append(subout)
    return out


def extract_anarchy(
    overview: QueryResponse, detailed_battles: list[QueryResponse]
) -> list[VsExtractDict]:
    overview_data = extract_overview_anarchy(overview)
    return build_vs_extract(detailed_battles, overview_data)


def extract_xbattle(
    overview: QueryResponse, detailed_battles: list[QueryResponse]
) -> list[VsExtractDict]:
    overview_data = extract_overview_xbattle(overview)
    return build_vs_extract(detailed_battles, overview_data)
