import datetime as dt
from typing import cast

from data_zipcaster.constants import MODES
from data_zipcaster.models import main, splatnet
from data_zipcaster.transforms.splatnet_to_main.players import convert_player
from data_zipcaster.utils import base64_decode, color_from_percent_to_str


def convert_mode(mode_id: str) -> main.ModeType:
    """Converts the mode ID to a mode type.

    This method converts the mode ID to a mode. First the mode ID is decoded
    from base64, then the mode ID is extracted from the decoded string. This
    mode ID is then compared against a lookup table of mode IDs to mode types,
    and the mode type is returned. Below are the values of the ``mode_id`` and
    the corresponding ``ModeType``.

    - ``1``: ``regular`` (Turf War)
    - ``2``: ``bankara_challenge`` (Anarchy Series)
    - ``3``: ``xbattle`` (Xbattle)
    - ``4``: ``league`` (Challenges)
    - ``5``: ``private`` (Private Battle)
    - ``51``: ``bankara_open`` (Anarchy Open)
    - ``6``: ``splatfest_open`` (Splatfest Open)
    - ``7``: ``splatfest_challenge`` (Splatfest Pro)
    - ``8``: ``splatfest_open`` (Splatfest Tricolor)

    Args:
        mode_id (str): The raw, unprocessed mode ID.

    Returns:
        main.ModeType: The mode of the battle. This is not to be confused with
            the rule of the battle, which is what is commonly referred to as the
            mode. This is confusing, but is the terminology used by SplatNet 3.
            One of ``regular``, ``bankara_challenge``, ``xbattle``, ``league``,
            ``private``, ``bankara-open``, ``splatfest_open``,
            ``splatfest_challenge``, or ``splatfest_open``.
    """
    mode_idx = base64_decode(mode_id)[len("VsMode-") :]
    return cast(main.ModeType, MODES.get_mode_by_id(mode_idx)["key"])


def convert_rule(rule: splatnet.RuleType) -> main.RuleType:
    """Converts the rule string to a rule type.

    This method converts the rule string to a rule type. This is done by
    comparing the rule string to a lookup table of rule strings to rule types.
    Below are the values of the ``rule`` and the corresponding ``RuleType``.

    - ``TURF_WAR``: ``turf_war``
    - ``AREA``: ``splat_zones``
    - ``LOFT``: ``tower_control``
    - ``GOAL``: ``rainmaker``
    - ``CLAM``: ``clam_blitz``
    - ``TRICOLOR``: ``tricolor``

    Args:
        rule (splatnet.RuleType): The raw, unprocessed rule string.

    Returns:
        main.RuleType: The rule of the battle. This is not to be confused with
            the mode of the battle, which is what is commonly referred to as the
            mode. This is confusing, but is the terminology used by SplatNet 3.
            One of ``turf_war``, ``splat_zones``, ``tower_control``,
            ``rainmaker``, ``clam_blitz``, or ``tricolor``.
    """
    rule_remap: dict[splatnet.RuleType, main.RuleType] = {
        "TURF_WAR": "turf_war",
        "AREA": "splat_zones",
        "LOFT": "tower_control",
        "GOAL": "rainmaker",
        "CLAM": "clam_blitz",
        "TRICOLOR": "tricolor",
    }
    return rule_remap[rule]


def convert_stage(stage_id: str) -> str:
    """Converts the stage ID to a stage name.

    This method converts the stage ID to a stage name. First the stage ID is
    decoded from base64, then the stage ID is extracted from the decoded string.

    Args:
        stage_id (str): The raw, unprocessed stage ID.

    Returns:
        str: The stage name. This is the stage's ID, everything after
            ``VsStage-`` in the base64-decoded stage ID.
    """
    return base64_decode(stage_id)[len("VsStage-") :]


def convert_result(
    judgement: splatnet.ResultType,
) -> main.ResultType:
    """Converts the judgement to a result type.

    Args:
        judgement (splatnet.ResultType): The raw, unprocessed judgement.

    Returns:
        main.ResultType: The result of the battle. One of ``win``, ``lose``,
            ``draw``, ``exempted_lose``, or ``deemed_lose``.
    """
    result_remap: dict[splatnet.ResultType, main.ResultType] = {
        "WIN": "win",
        "LOSE": "lose",
        "DRAW": "draw",
        "EXEMPTED_LOSE": "exempted_lose",
        "DEEMED_LOSE": "deemed_lose",
    }
    return result_remap[judgement]


def convert_start_time(start_time: str) -> dt.datetime:
    """Converts the start time to a datetime.

    The start time is in ISO 8601 format, but with the timezone offset
    replaced with ``Z``. This method converts the start time to a datetime
    object.

    Args:
        start_time (str): The raw, unprocessed start time.

    Returns:
        dt.datetime: The start time of the battle.
    """
    return dt.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")


def convert_duration(duration: int) -> dt.timedelta:
    """Converts the duration to a timedelta.

    The duration is in seconds. This method converts the duration to a
    timedelta object.

    Args:
        duration (int): The raw, unprocessed duration. An integer representing
            the duration in seconds.

    Returns:
        dt.timedelta: The duration of the battle.
    """
    return dt.timedelta(seconds=duration)


def get_teams_data(
    vs_detail: splatnet.VsDetail,
) -> list[splatnet.Team]:
    """Gets the teams data from the vs detail. This is a helper method that
    gets the teams data from the vs detail to reduce code duplication.

    Args:
        vs_detail (splatnet.VsDetail): The full vs detail model.

    Returns:
        list[splatnet.Team]: The teams data from the vs detail.
    """
    return [
        vs_detail.vsHistoryDetail.myTeam,
        *vs_detail.vsHistoryDetail.otherTeams,
    ]


def convert_tricolor_role(
    role: splatnet.TricolorRoleType | None,
) -> main.TricolorRoleType | None:
    """Converts the tricolor role to a tricolor role type.

    Simply turns the input to lowercase, but is a separate method for typing
    purposes.

    Args:
        role (splatnet.TricolorRoleType | None): The raw, unprocessed tricolor
            role.

    Returns:
        main.TricolorRoleType | None: The tricolor role type. One of
            ``defense``, ``attack1``, or ``attack2``.
    """
    if role is None:
        return None

    remap: dict[splatnet.TricolorRoleType, main.TricolorRoleType] = {
        "DEFENSE": "defense",
        "ATTACK1": "attack1",
        "ATTACK2": "attack2",
    }
    return remap[role]


def convert_team_data(vs_detail: splatnet.VsDetail) -> list[main.Team]:
    """Extracts the team data from the vs detail and converts it to a list of
    the main team model.

    Args:
        vs_detail (splatnet.VsDetail): The full vs detail model.

    Returns:
        list[main.Team]: The team data from the vs detail.
    """
    teams = get_teams_data(vs_detail)
    out: list[main.Team] = []

    for team in teams:
        sub_out = main.Team(
            players=[
                convert_player(player, idx)
                for idx, player in enumerate(team.players)
            ],
            color=color_from_percent_to_str(team.color.model_dump()),
            order=team.order,
        )

        if team.result is not None:
            assert team.judgement is not None
            sub_out.result = main.TeamResult(
                paint_ratio=team.result.paintRatio,
                score=team.result.score,
                noroshi=team.result.noroshi,
                team_result=convert_result(team.judgement),
            )

        if team.festTeamName is not None:
            sub_out.splatfest = main.SplatfestTeam(
                team_name=team.festTeamName,
                synergy_bonus=team.festUniformBonusRate,
                synergy_name=team.festUniformName,
                tricolor_role=convert_tricolor_role(team.tricolorRole),
            )

        out.append(sub_out)
    return out


def convert_knockout(
    knockout: splatnet.KnockoutType | None,
) -> main.KnockoutType:
    """Converts the knockout to a knockout type.

    Simply turns the input to lowercase, but is a separate method for typing
    purposes.

    Args:
        knockout (splatnet.KnockoutType | None): The raw, unprocessed knockout.

    Returns:
        main.KnockoutType: The knockout type. One of ``win``, ``lose``, or
            ``neither``.
    """
    if knockout is None:
        return None
    knockout_remap: dict[splatnet.KnockoutType, main.KnockoutType] = {
        "WIN": "win",
        "LOSE": "lose",
        "NEITHER": "neither",
    }
    return knockout_remap[knockout]


def convert_award(award: splatnet.Award) -> main.Awards:
    """Converts the award to an award model.

    Simply turns the input to lowercase, but is a separate method for typing
    purposes.

    Args:
        award (splatnet.Award): The raw, unprocessed award.

    Returns:
        main.Awards: The award model.
    """
    rank_remap: dict[splatnet.AwardRankType, main.AwardRankType] = {
        "GOLD": "gold",
        "SILVER": "silver",
    }
    return main.Awards(
        name=award.name,
        rank=rank_remap[award.rank],
    )


def convert_match_multiplier(
    match_multiplier: splatnet.MatchMultiplierType,
) -> main.MatchMultiplierType:
    """Converts the match multiplier to a match multiplier type.

    The following is a table of the match multiplier and the corresponding
    match multiplier type.

    - ``NORMAL``: ``1``
    - ``DECUPLE``: ``10``
    - ``DRAGON``: ``100``
    - ``DOUBLE_DRAGON``: ``333``

    Args:
        match_multiplier (splatnet.MatchMultiplierType): The raw, unprocessed
            match multiplier.

    Returns:
        main.MatchMultiplierType: The match multiplier type. One of ``1``,
            ``10``, ``100``, or ``333``.
    """
    match_multiplier_remap: dict[
        splatnet.MatchMultiplierType, main.MatchMultiplierType
    ] = {
        "NORMAL": 1,
        "DECUPLE": 10,
        "DRAGON": 100,
        "DOUBLE_DRAGON": 333,
    }
    return match_multiplier_remap[match_multiplier]
