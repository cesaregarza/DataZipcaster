from typing import cast

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.common import parse_result
from data_zipcaster.importers.splatnet.paths import overview_paths
from data_zipcaster.schemas.overview import (
    AnarchyOpenOverviewDict,
    AnarchyOverviewDict,
    AnarchyOverviewOut,
    AnarchySeriesOverviewDict,
    XOverviewDict,
)
from data_zipcaster.utils import base64_decode, cast_qr, parse_rank


def extract_overview_anarchy(
    overview: QueryResponse,
) -> dict[str, AnarchyOverviewDict]:
    """Extracts the Anarchy metadata from the "Overview" data from SplatNet 3.

    Given the "Overview" data from SplatNet 3, this function extracts the
    Anarchy metadata from the data. This contains various metadata about the
    Anarchy battles. This includes the following data:

    - ``rank_before``: The rank before the battle.
    - ``rank_after``: The rank after the battle.
    - ``rank_before_s_plus`` (optional): The S+ rank before the battle.
    - ``rank_after_s_plus`` (optional): The S+ rank after the battle.
    - ``rank_exp_change`` (optional): The change in rank experience.

    If the battle is an Anarchy Series battle, then the following data is also
    included:

    - ``series_win_count``: The number of wins in the series as of this battle.
    - ``series_lose_count``: The number of losses in the series as of this
        battle.
    - ``is_rank_up`` (optional): Whether the series is a rank up series.

    Args:
        overview (QueryResponse): The overview of Anarchy data, from the
            ``splatnet3_scraper`` query ``get_vs_battles``.

    Returns:
        dict[str, AnarchyOverviewDict]: A dictionary of ``AnarchyOverviewDict``
            objects, keyed by the battle ID. This is the internal representation
            of the data that importers convert to and exporters convert from.
    """
    out: dict[str, AnarchyOverviewDict] = {}
    for group in overview[overview_paths.A_HISTORY_GROUPS]:
        group = cast_qr(group)
        try:
            group_out: AnarchyOverviewOut = extract_anarchy_series_data(group)
        except TypeError:
            # Anarchy Open has no series data
            group_out = extract_anarchy_open(group)
        out.update(group_out)
    return out


def extract_anarchy_series_data(
    overview_group: QueryResponse,
) -> dict[str, AnarchySeriesOverviewDict]:
    """Extracts the Anarchy Series metadata from the "Overview" data from
    SplatNet 3.

    Given the "Overview" data from SplatNet 3, this function extracts the
    Anarchy Series metadata from the data. This contains various metadata about
    the Anarchy Series battles. This includes the following data:

    - ``rank_before``: The rank before the battle.
    - ``rank_after``: The rank after the battle.
    - ``rank_before_s_plus`` (optional): The S+ rank before the battle.
    - ``rank_after_s_plus`` (optional): The S+ rank after the battle.
    - ``rank_exp_change`` (optional): The change in rank experience.
    - ``is_rank_up`` (optional): Whether the series is a rank up series.
    - ``series_win_count``: The number of wins in the series as of this battle.
    - ``series_lose_count``: The number of losses in the series as of this
        battle.

    Args:
        overview_group (QueryResponse): The overview of Anarchy data, from the
            ``splatnet3_scraper`` query ``get_vs_battles``. This is a single
            series.

    Returns:
        dict[str, AnarchySeriesOverviewDict]: A dictionary of
            ``AnarchySeriesOverviewDict`` objects, keyed by the battle ID. This
            is the internal representation of the data that importers convert
            to and exporters convert from.
    """
    out: dict[str, AnarchySeriesOverviewDict] = {}

    try:
        rank_after, s_rank_after = parse_rank(
            overview_group[overview_paths.A_RANK_AFTER]
        )
    except AttributeError:
        # In-progress series
        rank_after, s_rank_after = None, None

    # Series metadata
    group_matches = cast_qr(overview_group[overview_paths.HISTORY_DETAILS])
    win_count = cast(int, overview_group[overview_paths.A_WIN_COUNT])
    lose_count = cast(int, overview_group[overview_paths.A_LOSE_COUNT])
    rank_points = cast(int, overview_group[overview_paths.A_EARNED_RANK_POINTS])
    is_rank_up = cast(bool, overview_group[overview_paths.A_IS_RANK_UP])

    # Parse the series data in reverse order
    for idx, match in enumerate(group_matches):
        match = cast_qr(match)
        battle_id = base64_decode(cast(str, match["id"]))
        # idx of 0 is the last match in the series, which has the rank after
        # if the series is over. Otherwise, parse the match as normal.
        if (idx == 0) and (rank_after is not None):
            sub_out = parse_a_last_match_series(
                match=match,
                rank_after=rank_after,
                s_rank_after=s_rank_after,
                win_count=win_count,
                lose_count=lose_count,
                rank_points=rank_points,
                is_rank_up=is_rank_up,
            )
        else:
            sub_out = parse_a_match_series(
                match=match,
                win_count=win_count,
                lose_count=lose_count,
            )

        # Update the running win/loss count. The last match in the series should
        # have a win/loss count of 0/0.
        judgement_str = cast(str, match[overview_paths.NODE_JUDGEMENT])
        judgement = parse_result(judgement_str)
        if judgement == "win":
            win_count -= 1
        elif judgement == "lose":
            lose_count -= 1

        out[battle_id] = sub_out
    return out


def extract_anarchy_open(
    overview_group: QueryResponse,
) -> dict[str, AnarchyOpenOverviewDict]:
    """Extracts the Anarchy Open metadata from the "Overview" data from
    SplatNet 3.

    Given the "Overview" data from SplatNet 3, this function extracts the
    Anarchy Open metadata from the data. This contains various metadata about
    the Anarchy Open battles. This includes the following data:

    - ``rank_before``: The rank before the battle.
    - ``rank_after``: The rank after the battle.
    - ``rank_before_s_plus`` (optional): The S+ rank before the battle.
    - ``rank_after_s_plus`` (optional): The S+ rank after the battle.
    - ``rank_exp_change`` (optional): The change in rank experience.

    Args:
        overview_group (QueryResponse): The overview of Anarchy Open data, from
            the ``splatnet3_scraper`` query ``get_vs_battles``. Realistically,
            this is a single battle.

    Returns:
        dict[str, AnarchyOpenOverviewDict]: A dictionary of
            ``AnarchyOpenOverviewDict`` objects, keyed by the battle ID. This
            is the internal representation of the data that importers convert
            to and exporters convert from.
    """
    out: dict[str, AnarchyOpenOverviewDict] = {}

    group_matches = cast_qr(overview_group[overview_paths.HISTORY_DETAILS])

    # Anarchy Open has no series metadata, so we just parse the matches in
    # reverse order.
    for match in group_matches:
        match = cast_qr(match)
        battle_id = base64_decode(cast(str, match["id"]))
        rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()

        rank_before, s_rank_before = parse_rank(rank_before_str)
        rank_points = cast(int, match[overview_paths.A_OPEN_EARNED_RANK_POINTS])

        subout = AnarchyOpenOverviewDict(
            rank_before=rank_before,
            rank_after=rank_before,
            rank_exp_change=rank_points,
        )
        if s_rank_before is not None:
            subout["rank_before_s_plus"] = s_rank_before
            subout["rank_after_s_plus"] = s_rank_before
        out[battle_id] = subout
    return out


def parse_a_last_match_series(
    match: QueryResponse,
    rank_after: str,
    s_rank_after: int | None,
    win_count: int,
    lose_count: int,
    rank_points: int,
    is_rank_up: bool,
) -> AnarchySeriesOverviewDict:
    """Parses the last match in an Anarchy series.

    This function parses the last match in an Anarchy series. This is a special
    case, as the last match in the series will have the overall result of the
    series, as well as the rank after the series.

    Args:
        match (QueryResponse): The match data.
        rank_after (str): The rank after the series is over.
        s_rank_after (int | None): The S+ rank after the series is over. This
            is ``None`` if the player is not at least S+0.
        win_count (int): The number of wins in the series at the end of the
            series.
        lose_count (int): The number of losses in the series at the end of the
            series.
        rank_points (int): The number of rank points earned in the series.
        is_rank_up (bool): Whether the series is a rank-up series.

    Returns:
        AnarchySeriesOverviewDict: The parsed data.
    """
    rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()
    rank_before, s_rank_before = parse_rank(rank_before_str)
    # Series metadata
    out = AnarchySeriesOverviewDict(
        rank_before=rank_before,
        rank_after=rank_after,
        rank_exp_change=rank_points,
        is_rank_up=is_rank_up,
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if s_rank_before is not None:
        out["rank_before_s_plus"] = s_rank_before
    if s_rank_after is not None:
        out["rank_after_s_plus"] = s_rank_after
    return out


def parse_a_match_series(
    match: QueryResponse, win_count: int, lose_count: int
) -> AnarchySeriesOverviewDict:
    """Parses a match in an Anarchy series.

    This function parses a match in an Anarchy series.

    Args:
        match (QueryResponse): The match data.
        win_count (int): The number of wins at this point in the series.
        lose_count (int): The number of losses at this point in the series.

    Returns:
        AnarchySeriesOverviewDict: The parsed data.
    """
    rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()
    rank_before, s_rank_before = parse_rank(rank_before_str)
    out = AnarchySeriesOverviewDict(
        rank_before=rank_before,
        rank_after=rank_before,
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if s_rank_before is not None:
        out["rank_before_s_plus"] = s_rank_before
        out["rank_after_s_plus"] = s_rank_before
    return out


def extract_overview_xbattle(
    overview: QueryResponse,
) -> dict[str, XOverviewDict]:
    """Extracts the Xbattle metadata from the "Overview" data from SplatNet 3.

    Given the "Overview" data from SplatNet 3, this function extracts the
    Xbattle metadata from the data. This contains various metadata about the
    Xbattles. This includes the following data:

    - ``series_win_count``: The number of wins at this point in the series.
    - ``series_lose_count``: The number of losses at this point in the series.
    - ``x_power_after`` (optional): The X Power after the match. This is not
        present if the battle is not the last battle in the series.

    Args:
        overview (QueryResponse): The "Overview" data from SplatNet 3.

    Returns:
        dict[str, XOverviewDict]: A dictionary of ``XOverviewDict`` objects,
            keyed by battle ID. This is the internal representation of the data
            that importers convert to and exporters convert from.
    """
    out = {}
    for group in overview[overview_paths.X_HISTORY_GROUPS]:
        group = cast(QueryResponse, group)
        group_out = extract_x_match_group(group)
        out.update(group_out)
    return out


def extract_x_match_group(group: QueryResponse) -> dict[str, XOverviewDict]:
    """Extracts the Xbattle metadata from the "Overview" data from SplatNet 3.

    Given the "Overview" data from SplatNet 3, this function extracts the
    Xbattle metadata from the data. This contains various metadata about the
    Xbattles. This includes the following data:

    - ``series_win_count``: The number of wins at this point in the series.
    - ``series_lose_count``: The number of losses at this point in the series.
    - ``x_power_after`` (optional): The X Power after the match. This is not
        present if the battle is not the last battle in the series.

    Args:
        group (QueryResponse): The "Overview" data from SplatNet 3.

    Returns:
        dict[str, XOverviewDict]: A dictionary of ``XOverviewDict`` objects,
            keyed by battle ID. This is the internal representation of the data
            that importers convert to and exporters convert from.
    """
    out = {}

    group_matches = cast(QueryResponse, group[overview_paths.HISTORY_DETAILS])
    win_count = cast(int, group[overview_paths.X_WIN_COUNT])
    lose_count = cast(int, group[overview_paths.X_LOSE_COUNT])
    x_power_after = cast(float | None, group[overview_paths.X_POWER_AFTER])

    for idx, match in enumerate(group_matches):
        match = cast(QueryResponse, match)
        battle_id = base64_decode(match["id"])
        sub_out = parse_x_match_series(
            x_power_after=x_power_after if idx == 0 else None,
            win_count=win_count,
            lose_count=lose_count,
        )
        judgement_str = cast(str, match[overview_paths.NODE_JUDGEMENT])
        judgement = parse_result(judgement_str)
        if judgement == "win":
            win_count -= 1
        elif judgement == "lose":
            lose_count -= 1

        out[battle_id] = sub_out
    return out


def parse_x_match_series(
    x_power_after: float | None,
    win_count: int,
    lose_count: int,
) -> XOverviewDict:
    """Parses a match in an Xbattle series.

    This function parses a match in an Xbattle series.

    Args:
        x_power_after (float | None): The X Power after the match. This is not
            present if the battle is not the last battle in the series.
        win_count (int): The number of wins at this point in the series.
        lose_count (int): The number of losses at this point in the series.

    Returns:
        XOverviewDict: The parsed data.
    """
    out = XOverviewDict(
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if x_power_after is not None:
        out["x_power_after"] = x_power_after
    return out
