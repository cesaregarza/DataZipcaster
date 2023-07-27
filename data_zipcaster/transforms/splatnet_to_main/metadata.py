from typing import TypeAlias

from data_zipcaster.models.main import (
    AnarchyOpenMetadata,
    AnarchySeriesMetadata,
    XMetadata,
)
from data_zipcaster.models.splatnet import (
    AnarchyMetaData as splatnet_AnarchyMetaData,
)
from data_zipcaster.models.splatnet import XMetaData as splatnet_XMetaData
from data_zipcaster.models.splatnet.typing.history_groups import (
    GroupNodeItems,
    NodeItems,
)
from data_zipcaster.utils import base64_decode, parse_rank

AnarchyMetadata: TypeAlias = AnarchyOpenMetadata | AnarchySeriesMetadata


def convert_anarchy_metadata(
    metadata: splatnet_AnarchyMetaData,
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
    group: GroupNodeItems,
) -> dict[str, AnarchySeriesMetadata]:
    out: dict[str, AnarchySeriesMetadata] = {}
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
    rank_points = group.bankaraMatchChallenge.earnedUdemaePoint
    is_rank_up = group.bankaraMatchChallenge.isUdemaeUp

    assert rank_points is not None
    assert is_rank_up is not None

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
                rank_points=rank_points,
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
    match: NodeItems,
    rank_after: str,
    s_rank_after: int | None,
    win_count: int,
    lose_count: int,
    rank_points: int,
    is_rank_up: bool,
) -> AnarchySeriesMetadata:
    assert match.udemae is not None
    assert match.bankaraMatch is not None
    assert match.bankaraMatch.earnedUdemaePoint is not None

    rank_before, s_rank_before = parse_rank(match.udemae.lower())
    rank_points = match.bankaraMatch.earnedUdemaePoint
    out = AnarchySeriesMetadata(
        rank_before=rank_before,
        rank_after=rank_after,
        rank_exp_change=rank_points,
        is_rank_up=is_rank_up,
        series_win_count=win_count,
        series_lose_count=lose_count,
    )
    if s_rank_before is not None:
        out.rank_before_s_plus = s_rank_before
    if s_rank_after is not None:
        out.rank_after_s_plus = s_rank_after
    return out


def parse_anarchy_series_match(
    match: NodeItems,
    win_count: int,
    lose_count: int,
) -> AnarchySeriesMetadata:
    assert match.udemae is not None
    rank_before, s_rank_before = parse_rank(match.udemae.lower())
    out = AnarchySeriesMetadata(
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
    group: GroupNodeItems,
) -> dict[str, AnarchyOpenMetadata]:
    out: dict[str, AnarchyOpenMetadata] = {}

    for match in group.historyDetails.nodes:
        assert match.bankaraMatch is not None
        assert match.udemae is not None
        assert match.bankaraMatch.earnedUdemaePoint is not None
        battle_id = base64_decode(match.id)
        rank_before, s_rank_before = parse_rank(match.udemae.lower())
        rank_points = match.bankaraMatch.earnedUdemaePoint

        subout = AnarchyOpenMetadata(
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
    metadata: splatnet_XMetaData,
) -> dict[str, XMetadata]:
    out: dict[str, XMetadata] = {}
    for group in metadata.xBattleHistories.historyGroups.nodes:
        assert group.xMatchMeasurement is not None

        group_matches = group.historyDetails.nodes
        win_count = group.xMatchMeasurement.winCount
        lose_count = group.xMatchMeasurement.loseCount
        x_power_after = group.xMatchMeasurement.xPowerAfter

        for idx, match in enumerate(group_matches):
            battle_id = base64_decode(match.id)
            sub_out = XMetadata(
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
