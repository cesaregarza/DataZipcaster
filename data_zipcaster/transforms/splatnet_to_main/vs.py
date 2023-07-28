from typing import TypeAlias

from data_zipcaster.models import main, splatnet
from data_zipcaster.transforms.splatnet_to_main.common import (
    convert_award,
    convert_duration,
    convert_knockout,
    convert_match_multiplier,
    convert_mode,
    convert_result,
    convert_rule,
    convert_stage,
    convert_start_time,
    convert_team_data,
)
from data_zipcaster.utils import base64_decode

SeriesMetadata: TypeAlias = main.XMetadata | main.AnarchySeriesMetadata


def convert_vs_data(vs_detail: splatnet.VsDetail) -> main.VsExtract:
    """Converts a ``VsDetail`` object to a ``VsExtract`` object.

    This function converts a ``VsDetail`` object from the SplatNet 3 API to a
    ``VsExtract`` object, which is the internal representation of battle data
    that importers convert to and exporters convert from.

    Args:
        vs_detail (splatnet.VsDetail): The ``VsDetail`` object to convert.

    Returns:
        main.VsExtract: The converted ``VsExtract`` object.
    """
    teams = convert_team_data(vs_detail)
    match_id = base64_decode(vs_detail.vsHistoryDetail.id)
    mode = convert_mode(vs_detail.vsHistoryDetail.vsMode.id)
    assert vs_detail.vsHistoryDetail.vsRule.rule is not None
    out = main.VsExtract(
        knockout=convert_knockout(vs_detail.vsHistoryDetail.knockout),
        mode=mode,
        result=convert_result(vs_detail.vsHistoryDetail.judgement),
        rule=convert_rule(vs_detail.vsHistoryDetail.vsRule.rule),
        stage=convert_stage(vs_detail.vsHistoryDetail.vsStage.id),
        start_time=convert_start_time(vs_detail.vsHistoryDetail.playedTime),
        duration=convert_duration(vs_detail.vsHistoryDetail.duration),
        teams=teams,
        awards=[
            convert_award(award) for award in vs_detail.vsHistoryDetail.awards
        ],
        id=match_id,
    )

    if mode == "bankara_open":
        assert vs_detail.vsHistoryDetail.bankaraMatch is not None
        out.match_power = vs_detail.vsHistoryDetail.bankaraMatch.bankaraPower
    elif mode == "league":
        assert vs_detail.vsHistoryDetail.leagueMatch is not None
        out.match_power = vs_detail.vsHistoryDetail.leagueMatch.myLeaguePower
        out.challenge_id = base64_decode(
            vs_detail.vsHistoryDetail.leagueMatch.leagueMatchEvent.id
        )
    elif mode == "splatfest_challenge":
        assert vs_detail.vsHistoryDetail.festMatch is not None
        out.splatfest_metadata = main.SplatfestMetadata(
            match_multiplier=convert_match_multiplier(
                vs_detail.vsHistoryDetail.festMatch.dragonMatchType
            ),
            clout=vs_detail.vsHistoryDetail.festMatch.contribution,
            jewel=vs_detail.vsHistoryDetail.festMatch.jewel,
        )
    elif mode == "xbattle":
        assert vs_detail.vsHistoryDetail.xMatch is not None
        out.match_power = vs_detail.vsHistoryDetail.xMatch.lastXPower

    return out


def append_metadata(
    vs_extract: main.VsExtract, metadata_ref: dict[str, SeriesMetadata]
) -> main.VsExtract:
    """Appends metadata to a ``VsExtract`` object.

    This function appends metadata to a ``VsExtract`` object, which is the
    internal representation of battle data that importers convert to and
    exporters convert from.

    Args:
        vs_extract (main.VsExtract): The ``VsExtract`` object to append metadata
            to.
        metadata_ref (dict[SeriesMetadata]): A dictionary of metadata, keyed by
            battle ID.

    Returns:
        main.VsExtract: The ``VsExtract`` object with metadata appended.
    """
    if vs_extract.id in metadata_ref:
        vs_extract.series_metadata = metadata_ref[vs_extract.id]
    return vs_extract
