from typing import cast

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.common import (
    extract_mode,
    parse_result,
)
from data_zipcaster.importers.splatnet.paths import overview_paths
from data_zipcaster.utils import parse_rank


def extract_overview_anarchy(overview: QueryResponse) -> dict[str, dict]:
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
    out = {}
    for group in overview[overview_paths.A_HISTORY_GROUPS]:
        group = cast(QueryResponse, group)
        try:
            group_out = extract_anarchy_series_data(group)
        except TypeError as e:
            # Anarchy Open has no series data
            group_out = extract_anarchy_open(group)
        out.update(group_out)
    return out


def extract_anarchy_series_data(overview_group: QueryResponse) -> dict:
    out = {}

    try:
        rank_after, s_rank_after = parse_rank(
            overview_group[overview_paths.A_RANK_AFTER]
        )
    except AttributeError:
        # In-progress series
        rank_after, s_rank_after = None, None

    group_matches = cast(
        QueryResponse, overview_group[overview_paths.HISTORY_DETAILS]
    )
    win_count = cast(int, overview_group[overview_paths.A_WIN_COUNT])
    lose_count = cast(int, overview_group[overview_paths.A_LOSE_COUNT])

    for idx, match in enumerate(group_matches):
        match = cast(QueryResponse, match)
        battle_id = match["id"]
        sub_out = {}
        if (idx == 0) and (rank_after is not None):
            sub_out = parse_a_last_match_series(
                match=match,
                rank_after=rank_after,
                s_rank_after=s_rank_after,
                win_count=win_count,
                lose_count=lose_count,
                rank_points=cast(
                    int, overview_group[overview_paths.A_EARNED_RANK_POINTS]
                ),
                is_rank_up=cast(
                    bool, overview_group[overview_paths.A_IS_RANK_UP]
                ),
            )
        else:
            sub_out = parse_a_match_series(
                match=match,
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


def extract_anarchy_open(overview_group: QueryResponse) -> dict:
    out = {}
    group_matches = cast(
        QueryResponse, overview_group[overview_paths.HISTORY_DETAILS]
    )
    for match in group_matches:
        match = cast(QueryResponse, match)
        battle_id = match["id"]
        rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()
        rank_before, s_rank_before = parse_rank(rank_before_str)
        rank_points = cast(int, match[overview_paths.A_OPEN_EARNED_RANK_POINTS])
        subout = {
            "rank_before": rank_before,
            "rank_before_s_plus": s_rank_before,
            "rank_after": rank_before,
            "rank_after_s_plus": s_rank_before,
            "rank_exp_change": rank_points,
        }
        if s_rank_before is None:
            subout.pop("rank_before_s_plus")
            subout.pop("rank_after_s_plus")
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
) -> dict:
    rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()
    rank_before, s_rank_before = parse_rank(rank_before_str)
    return {
        "rank_before": rank_before,
        "rank_before_s_plus": s_rank_before,
        "rank_after": rank_after,
        "rank_after_s_plus": s_rank_after,
        "rank_exp_change": rank_points,
        "is_rank_up": "yes" if is_rank_up else "no",
        "challenge_win": win_count,
        "challenge_lose": lose_count,
    }


def parse_a_match_series(
    match: QueryResponse, win_count: int, lose_count: int
) -> dict:
    rank_before_str = cast(str, match[overview_paths.NODE_RANK]).lower()
    rank_before, s_rank_before = parse_rank(rank_before_str)
    return {
        "rank_before": rank_before,
        "rank_before_s_plus": s_rank_before,
        "rank_after": rank_before,
        "rank_after_s_plus": s_rank_before,
        "challenge_win": win_count,
        "challenge_lose": lose_count,
    }


def parse_judgement(judgement: str) -> str:
    match judgement.lower():
        case "win" | "lose" | "exempted_lose" | "draw":
            return judgement.lower()
        case "deemed_lose":
            return "lose"
        case _:
            raise ValueError(f"Unknown judgement: {judgement}")


def parse_x_match_series(
    x_power_after: float | None,
    x_power_before: float | None,
    win_count: int,
    lose_count: int,
) -> dict:
    out = {
        "x_power_before": x_power_before,
        "x_power_after": x_power_after,
        "challenge_win": win_count,
        "challenge_lose": lose_count,
    }
    if x_power_after is None:
        out.pop("x_power_after")
    if x_power_before is None:
        out.pop("x_power_before")
    return out
