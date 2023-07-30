from typing import TypeAlias

from data_zipcaster.models import main, splatnet
from data_zipcaster.utils import base64_decode, parse_rank

AnarchyMetadata: TypeAlias = (
    main.AnarchyOpenMetadata | main.AnarchySeriesMetadata
)

Metadata: TypeAlias = main.AnarchyMetadata | main.XMetadata


def convert_anarchy_metadata(
    metadata: splatnet.AnarchyMetadata,
) -> dict[str, AnarchyMetadata]:
    out: dict[str, AnarchyMetadata] = {}
    for group in metadata.bankaraBattleHistories.historyGroups.nodes:
        # Check if the group is a series by checking if it has
        # bankaraMatchChallenge
        if group.bankaraMatchChallenge is not None:
            # This *must* be unpacked, mypy does not recognize that
            # dict[str, A] | dict[str, B] is dict[str, A | B] with the update
            # method, so we must unpack both dicts into a new dict to get the
            # correct type. This is not a mypy bug but a limitation of the
            # type system when dealing with mutable types.
            out = {**out, **convert_anarchy_series_metadata(group)}
        else:
            out = {**out, **convert_anarchy_open_metadata(group)}
    return out


def convert_anarchy_series_metadata(
    group: splatnet.GroupNodeItems,
) -> dict[str, main.AnarchySeriesMetadata]:
    out: dict[str, main.AnarchySeriesMetadata] = {}
    assert group.bankaraMatchChallenge is not None

    if group.bankaraMatchChallenge.udemaeAfter is None:
        rank_after, s_rank_after = None, None
    else:
        rank_after, s_rank_after = parse_rank(
            group.bankaraMatchChallenge.udemaeAfter
        )

    assert group.bankaraMatchChallenge is not None

    # Metadata
    win_count = group.bankaraMatchChallenge.winCount
    lose_count = group.bankaraMatchChallenge.loseCount
    is_rank_up = group.bankaraMatchChallenge.isUdemaeUp

    if is_rank_up is None:
        is_rank_up = False

    for idx, match in enumerate(group.historyDetails.nodes):
        battle_id = base64_decode(match.id)
        # idx of 0 is the last match in the series, which has the rank after
        # if the series is over. Otherwise, parse the match as normal.
        if (idx == 0) and (rank_after is not None):
            sub_out = parse_last_anarchy_series_match(
                match=match,
                rank_after=rank_after,
                s_rank_after=s_rank_after,
                win_count=win_count,
                lose_count=lose_count,
                is_rank_up=is_rank_up,
            )
        else:
            sub_out = parse_anarchy_series_match(
                match=match,
                win_count=win_count,
                lose_count=lose_count,
            )

        if match.judgement == "WIN":
            win_count -= 1
        elif match.judgement in ("LOSE", "DEEMED_LOSE"):
            lose_count -= 1

        out[battle_id] = sub_out
    return out


def parse_last_anarchy_series_match(
    match: splatnet.NodeItems,
    rank_after: str,
    s_rank_after: int | None,
    win_count: int,
    lose_count: int,
    is_rank_up: bool,
) -> main.AnarchySeriesMetadata:
    assert match.udemae is not None
    assert match.bankaraMatch is not None

    rank_before, s_rank_before = parse_rank(match.udemae.lower())
    out = main.AnarchySeriesMetadata(
        rank_before=rank_before,
        rank_after=rank_after,
        is_rank_up=is_rank_up,
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if s_rank_before is not None:
        out.rank_before_s_plus = s_rank_before
    if s_rank_after is not None:
        out.rank_after_s_plus = s_rank_after
    if match.bankaraMatch.earnedUdemaePoint is not None:
        out.rank_exp_change = match.bankaraMatch.earnedUdemaePoint

    return out


def parse_anarchy_series_match(
    match: splatnet.NodeItems,
    win_count: int,
    lose_count: int,
) -> main.AnarchySeriesMetadata:
    assert match.udemae is not None
    rank_before, s_rank_before = parse_rank(match.udemae.lower())
    out = main.AnarchySeriesMetadata(
        rank_before=rank_before,
        rank_after=rank_before,
        rank_exp_change=0,
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if s_rank_before is not None:
        out.rank_before_s_plus = s_rank_before
        out.rank_after_s_plus = s_rank_before
    return out


def convert_anarchy_open_metadata(
    group: splatnet.GroupNodeItems,
) -> dict[str, main.AnarchyOpenMetadata]:
    out: dict[str, main.AnarchyOpenMetadata] = {}

    for match in group.historyDetails.nodes:
        assert match.bankaraMatch is not None
        assert match.udemae is not None
        assert match.bankaraMatch.earnedUdemaePoint is not None
        battle_id = base64_decode(match.id)
        rank_before, s_rank_before = parse_rank(match.udemae.lower())
        rank_points = match.bankaraMatch.earnedUdemaePoint

        subout = main.AnarchyOpenMetadata(
            rank_before=rank_before,
            rank_after=rank_before,
            rank_exp_change=rank_points,
        )
        if s_rank_before is not None:
            subout.rank_before_s_plus = s_rank_before
            subout.rank_after_s_plus = s_rank_before
        out[battle_id] = subout
    return out


def convert_xbattle_metadata(
    metadata: splatnet.XMetadata,
) -> dict[str, main.XMetadata]:
    out: dict[str, main.XMetadata] = {}
    for group in metadata.xBattleHistories.historyGroups.nodes:
        assert group.xMatchMeasurement is not None

        group_matches = group.historyDetails.nodes
        win_count = group.xMatchMeasurement.winCount
        lose_count = group.xMatchMeasurement.loseCount
        x_power_after = group.xMatchMeasurement.xPowerAfter

        for idx, match in enumerate(group_matches):
            battle_id = base64_decode(match.id)
            sub_out = main.XMetadata(
                series_win_count=win_count,
                series_lose_count=lose_count,
            )
            if (idx == 0) and (x_power_after is not None):
                sub_out.x_power_after = x_power_after

            if match.judgement == "WIN":
                win_count -= 1
            elif match.judgement in ("LOSE", "DEEMED_LOSE"):
                lose_count -= 1

            out[battle_id] = sub_out
    return out


def convert_metadata(
    raw_metadata: splatnet.AnarchyMetadata | splatnet.XMetadata,
) -> dict[str, Metadata]:
    out: dict[str, Metadata] = {}
    if isinstance(raw_metadata, splatnet.AnarchyMetadata):
        out = {**out, **convert_anarchy_metadata(raw_metadata)}
    elif isinstance(raw_metadata, splatnet.XMetadata):
        out = {**out, **convert_xbattle_metadata(raw_metadata)}

    return out
