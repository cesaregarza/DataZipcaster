from typing import TypeAlias, cast

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.common import parse_result
from data_zipcaster.importers.splatnet.paths import overview_paths
from data_zipcaster.json_keys import anarchy as a_keys
from data_zipcaster.json_keys import xbattle as x_keys
from data_zipcaster.schemas.overview import (
    AnarchyOpenOverviewDict,
    AnarchyOverviewDict,
    AnarchyOverviewOut,
    AnarchySeriesOverviewDict,
    VsOverviewDict,
    XOverviewDict,
)
from data_zipcaster.schemas.typing import ResultType
from data_zipcaster.utils import cast_qr, parse_rank


def extract_overview_anarchy(
    overview: QueryResponse,
) -> dict[str, AnarchyOverviewDict]:
    """Extracts data from the overview of Anarchy data.

    Given a QueryResponse object containing the overview of Anarchy data, from
    the splatnet3_scraper query "get_vs_battles", this function extracts the
    data from the overview. This includes the following data:

    - ``rank_before``: The rank before the battle.
    - ``s_rank_before``: The S+ rank before the battle. If the player is not
        S+, this will be ``None``.
    - ``rank_after``: The rank after the battle.
    - ``s_rank_after``: The S+ rank after the battle. If the player is not
        S+, this will be ``None``.
    - ``is_rank_up``: Whether the series is a rank-up series.
    - ``challenge_win``: The number of wins so far in the challenge, after this
        battle is included.
    - ``challenge_lose``: The number of losses so far in the challenge, after
        this battle is included.
    - ``rank_exp_change`` (optional): The change in rank experience after the
        series. This is only present for the last battle once a series is over.

    Args:
        overview (QueryResponse): The overview of Anarchy data, from the
            ``splatnet3_scraper`` query ``get_vs_battles``.

    Returns:
        dict: A dictionary containing the extracted data. The keys are as

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
        battle_id = cast(str, match["id"])
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
    out: dict[str, AnarchyOpenOverviewDict] = {}

    group_matches = cast_qr(overview_group[overview_paths.HISTORY_DETAILS])

    # Anarchy Open has no series metadata, so we just parse the matches in
    # reverse order.
    for match in group_matches:
        match = cast_qr(match)
        battle_id = cast(str, match["id"])
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
    rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()
    rank_before, s_rank_before = parse_rank(rank_before_str)
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
    out = {}
    for group in overview[overview_paths.X_HISTORY_GROUPS]:
        group = cast(QueryResponse, group)
        group_out = extract_x_match_group(group)
        out.update(group_out)
    return out


def extract_x_match_group(group: QueryResponse) -> dict[str, XOverviewDict]:
    out = {}

    group_matches = cast(QueryResponse, group[overview_paths.HISTORY_DETAILS])
    win_count = cast(int, group[overview_paths.X_WIN_COUNT])
    lose_count = cast(int, group[overview_paths.X_LOSE_COUNT])
    x_power_after = cast(float | None, group[overview_paths.X_POWER_AFTER])

    for idx, match in enumerate(group_matches):
        match = cast(QueryResponse, match)
        battle_id = match["id"]
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
    out = XOverviewDict(
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if x_power_after is not None:
        out["x_power_after"] = x_power_after
    return out
