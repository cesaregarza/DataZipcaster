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
    """Builds a list of ``VsExtractDict`` objects from a list of detailed
    battles.

    Given a list of detailed battles, this function extracts the data from each
    battle and returns a list of ``VsExtractDict`` objects. If the overview data
    is provided, then the ``series_metadata`` field will be populated with the
    appropriate data. This is the internal representation of battle data that
    importers convert to and exporters convert from.

    Args:
        detailed_battles (list[QueryResponse]): A list of detailed battles, from
            the SplatNet 3 query ``VsHistoryDetailQuery``.
        overview_data (VsOverviewOut | None): The overview data for the battles.
            This is the output of the ``extract_overview_*`` functions. Defaults
            to ``None``.

    Returns:
        list[VsExtractDict]: A list of VsExtractDict objects, containing the
            extracted data from the battles.
    """
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
    """Extracts the data from a list of detailed battles for the Anarchy mode.

    Given an overview ``QueryResponse`` and a list of detailed battles, this
    function extracts the data from each battle and returns a list of
    ``VsExtractDict`` objects. This is the internal representation of battle
    data that importers convert to and exporters convert from.

    Args:
        overview (QueryResponse): The overview data for the battles, from the
            SplatNet 3 queries of the form ``*BattleHistoriesQuery``.
        detailed_battles (list[QueryResponse]): A list of detailed battles, from
            the SplatNet 3 query ``VsHistoryDetailQuery``.

    Returns:
        list[VsExtractDict]: A list of ``VsExtractDict`` objects, containing the
            extracted data from the battles.
    """
    overview_data = extract_overview_anarchy(overview)
    return build_vs_extract(detailed_battles, overview_data)


def extract_xbattle(
    overview: QueryResponse, detailed_battles: list[QueryResponse]
) -> list[VsExtractDict]:
    """Extracts the data from a list of detailed battles for the X Battle mode.

    Given an overview ``QueryResponse`` and a list of detailed battles, this
    function extracts the data from each battle and returns a list of
    ``VsExtractDict`` objects. This is the internal representation of battle
    data that importers convert to and exporters convert from.

    Args:
        overview (QueryResponse): The overview data for the battles, from the
            SplatNet 3 queries of the form ``*BattleHistoriesQuery``.
        detailed_battles (list[QueryResponse]): A list of detailed battles, from
            the SplatNet 3 query ``VsHistoryDetailQuery``.

    Returns:
        list[VsExtractDict]: A list of ``VsExtractDict`` objects, containing the
            extracted data from the battles.
    """
    overview_data = extract_overview_xbattle(overview)
    return build_vs_extract(detailed_battles, overview_data)
