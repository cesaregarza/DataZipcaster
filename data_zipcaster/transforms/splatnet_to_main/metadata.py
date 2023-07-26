from data_zipcaster.models.main import (
    AnarchyOpenMetadata,
    AnarchySeriesMetadata,
    XMetadata,
)
from data_zipcaster.models.splatnet import MetaData
from data_zipcaster.models.splatnet.typing.history_groups import (
    GroupNodeItems,
    NodeItems,
)
from data_zipcaster.transforms.splatnet_to_main.typing import AnarchyMetadata
from data_zipcaster.utils import base64_decode, parse_rank


def convert_anarchy_metadata(metadata: MetaData) -> AnarchyMetadata:
    out = {}
    for group in metadata.bankaraBattleHistories.historyGroups.nodes:
        # Check if the group is a series by checking if it has bankaraMatchChallenge
        if group.bankaraMatchChallenge is not None:
            group_out = convert_anarchy_series_metadata(group)
        else:
            group_out = convert_anarchy_open_metadata(group)


def convert_anarchy_series_metadata(
    group: GroupNodeItems,
) -> dict[str, AnarchySeriesMetadata]:
    out: dict[str, AnarchySeriesMetadata] = {}
    try:
        rank_after, s_rank_after = parse_rank(
            group.bankaraMatchChallenge.udemaeAfter
        )
    except AttributeError:
        rank_after, s_rank_after = None, None

    # Metadata
    win_count = group.bankaraMatchChallenge.winCount
    lose_count = group.bankaraMatchChallenge.loseCount
    rank_points = group.bankaraMatchChallenge.earnedUdemaePoint
    is_rank_up = group.bankaraMatchChallenge.isUdemaeUp

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
    s_rank_after: int,
    win_count: int,
    lose_count: int,
    rank_points: int,
    is_rank_up: bool,
) -> AnarchySeriesMetadata:
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
    rank_before, s_rank_before = parse_rank(match.udemae.lower())
    out = AnarchySeriesMetadata(
        rank_before=rank_before,
        rank_after=rank_before,
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
