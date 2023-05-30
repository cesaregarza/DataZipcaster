from typing import cast
from urllib.parse import urlparse

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.assets import GEAR_HASHES
from data_zipcaster.importers.splatnet.paths import gear_paths, player_paths
from data_zipcaster.utils import base64_decode


def extract_weapon_id(player: QueryResponse) -> int:
    weapon_id = cast(str, player[player_paths.WEAPON_ID])
    weapon_id = base64_decode(weapon_id)
    weapon_id = weapon_id[len("Weapon-") :]
    return int(weapon_id)


def extract_gear_stats(gear: QueryResponse) -> dict[str, str | list[str]]:
    def extract_stat(url: str) -> str:
        path = urlparse(url).path
        hash = path.split("/")[-1][:64]
        return GEAR_HASHES[hash]

    main_stat = extract_stat(cast(str, gear[gear_paths.PRIMARY_ABILITY]))
    sub_query_responses = cast(
        QueryResponse, gear[gear_paths.ADDITIONAL_ABILITIES]
    )
    sub_stats = []
    for sub in sub_query_responses:
        sub_url = cast(str, sub[gear_paths.ADDITIONAL_ABILITIES_URL])
        sub_stat = extract_stat(sub_url)
        sub_stats.append(sub_stat)
    return {
        "primary_ability": main_stat,
        "additional_abilities": sub_stats,
    }


def extract_gear(
    player: QueryResponse,
) -> dict[str, dict[str, str | list[str]]]:
    return {
        gear_path: extract_gear_stats(cast(QueryResponse, player[gear_path]))
        for gear_path in player_paths.GEARS
    }


def extract_player_data(
    player: QueryResponse, scoreboard_position: int
) -> dict[str, str | int | dict]:
    out = {}
    out["name"] = player[player_paths.NAME]
    out["me"] = player[player_paths.IS_MYSELF]
    if number := player.get(player_paths.PLAYER_NUMBER):
        out["player_number"] = str(number)

    out["splashtag"] = player[player_paths.SPLASHTAG]
    out["weapon"] = extract_weapon_id(player)
    out["inked"] = player[player_paths.INKED]
    out["species"] = cast(str, player[player_paths.SPECIES]).lower()
    out["scoreboard_position"] = scoreboard_position + 1
    out["gear"] = extract_gear(player)

    # The following fields are empty if the player disconnected
    if player.get(player_paths.RESULT) is None:
        out["disconnected"] = True
        return out

    out["kills_or_assists"] = player[player_paths.KILL_OR_ASSIST]
    out["assists"] = player[player_paths.ASSIST]
    out["kills"] = out["kills_or_assists"] - out["assists"]
    out["deaths"] = player[player_paths.DEATH]
    out["specials"] = player[player_paths.SPECIAL]
    out["signals"] = player[player_paths.SIGNAL]
    out["top_500_crown"] = player[player_paths.TOP_500_CROWN]
    out["disconnected"] = False
    return out
