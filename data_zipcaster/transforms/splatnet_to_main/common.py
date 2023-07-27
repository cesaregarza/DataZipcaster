import datetime as dt
import uuid
from typing import cast

from data_zipcaster.constants import MODES
from data_zipcaster.models.main import typing as main_typing
from data_zipcaster.models.main.players import Player as main_Player
from data_zipcaster.models.main.vs_modes import Team as main_Team
from data_zipcaster.models.splatnet import VsDetail
from data_zipcaster.models.splatnet.submodels import typing as splatnet_typing
from data_zipcaster.models.splatnet.submodels.players import (
    Player,
    PlayerRoot,
    Team,
)
from data_zipcaster.utils import base64_decode, color_from_percent_to_str


def generate_match_uuid(battle_id: str, namespace: uuid.UUID) -> str:
    """Generates a match UUID from a battle ID.

    Given a battle ID, this method will generate a match UUID. This is done
    according to stat.ink's documentation, which can be found
    `here <https://tinyurl.com/3atce4kw>`_. The UUID is generated using the
    ``uuid.uuid5`` method, which takes a namespace UUID and a name. The
    namespace UUID is provided by the user, and the name is the last 52
    characters of the battle ID. The last 52 characters of the battle ID are
    used since it contains the timestamp of the battle in the form
    ``YYYYMMDDTHHMMSS`` followed by a match uuid generated by Nintendo. This
    should ensure there are no collisions between match UUIDs.


    Args:
        battle_id (str): A (probably) unique ID for a battle. This is the
            ``id`` field of the ``vsHistoryDetail`` field of the response
            from a ``vsHistoryDetail`` query.
        namespace (uuid.UUID): The namespace UUID to use when generating the
            match UUID.

    Returns:
        str: The match UUID.
    """
    return str(uuid.uuid5(namespace, battle_id[-52:]))


def convert_mode(battle_id: str) -> main_typing.ModeType:
    mode_idx = base64_decode(battle_id)[len("VsMode-") :]
    return cast(main_typing.ModeType, MODES.get_mode_by_id(mode_idx)["key"])


def convert_rule(rule: splatnet_typing.RuleType) -> main_typing.RuleType:
    rule_remap: dict[splatnet_typing.RuleType, main_typing.RuleType] = {
        "TURF_WAR": "turf_war",
        "AREA": "splat_zones",
        "LOFT": "tower_control",
        "GOAL": "rainmaker",
        "CLAM": "clam_blitz",
        "TRICOLOR": "tricolor",
    }
    return rule_remap[rule]


def convert_stage(stage_id: str) -> str:
    return base64_decode(stage_id)[len("Stage-") :]


def convert_result(
    judgement: splatnet_typing.ResultType,
) -> main_typing.ResultType:
    result_remap: dict[splatnet_typing.ResultType, main_typing.ResultType] = {
        "WIN": "win",
        "LOSE": "lose",
        "DRAW": "draw",
        "EXEMPTED_LOSE": "exempted_lose",
        "DEEMED_LOSE": "deemed_lose",
    }
    return result_remap[judgement]


def convert_start_time(start_time: str) -> dt.datetime:
    return dt.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")


def convert_duration(duration: int) -> dt.timedelta:
    return dt.timedelta(seconds=duration)


def get_teams_data(
    vs_detail: VsDetail,
) -> list[Team]:
    return [
        vs_detail.vsHistoryDetail.myTeam,
        *vs_detail.vsHistoryDetail.otherTeams,
    ]


def convert_team_data(vs_detail: VsDetail) -> list[main_Team]:
    teams = get_teams_data(vs_detail)
    out: list[main_Team] = []

    for team in teams:
        players: list[main_Player] = []
        for idx, player in enumerate(team.players):
            # players.append(convert_player_data(player, idx))
            pass
