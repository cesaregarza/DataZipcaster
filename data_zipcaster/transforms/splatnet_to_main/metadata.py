from typing import TypeAlias, cast, Union

from data_zipcaster.models.main import (
    AnarchyOpenMetadata,
    AnarchySeriesMetadata,
    XMetadata,
)
from data_zipcaster.models.splatnet import (
    AnarchyMetaData as splatnet_AnarchyMetaData,
)
from data_zipcaster.models.splatnet import (
    ChallengeMetaData as splatnet_ChallengeMetaData,
)
from data_zipcaster.models.splatnet import TurfMetaData as splatnet_TurfMetaData
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
            # This *must* be unpacked
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
