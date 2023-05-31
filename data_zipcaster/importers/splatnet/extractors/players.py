from typing import cast
from urllib.parse import urlparse

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.assets import GEAR_HASHES
from data_zipcaster.importers.splatnet.paths import gear_paths, player_paths
from data_zipcaster.utils import base64_decode
from data_zipcaster.json_keys import players as players_keys


def extract_weapon_id(player: QueryResponse) -> int:
    """Extracts the weapon ID from a player's data.

    Args:
        player (QueryResponse): The player's data.

    Returns:
        int: The weapon ID.
    """
    weapon_id = cast(str, player[player_paths.WEAPON_ID])
    weapon_id = base64_decode(weapon_id)
    weapon_id = weapon_id[len("Weapon-") :]
    return int(weapon_id)


def extract_gear_stats(gear: QueryResponse) -> dict[str, str | list[str]]:
    """Extracts the gear stats from a player's gear.

    Args:
        gear (QueryResponse): The player's gear.

    Returns:
        dict[str, str | list[str]]: The gear stats. The keys are as follows:

        - ``primary_ability``: The primary ability.
        - ``additional_abilities``: A list of additional abilities.
    """

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
        players_keys.PRIMARY_ABILITY: main_stat,
        players_keys.ADDITIONAL_ABILITIES: sub_stats,
    }


def extract_gear(
    player: QueryResponse,
) -> dict[str, dict[str, str | list[str]]]:
    """Extracts the gear from a player's data.

    Args:
        player (QueryResponse): The player's data.

    Returns:
        dict[str, dict[str, str | list[str]]]: The gear. The keys are as
        follows:

        - ``headGear``: The headgear.
        - ``clothingGear``: The clothing.
        - ``shoesGear``: The shoes.

        The values are dicts with the following keys:

        - ``primary_ability``: The primary ability.
        - ``additional_abilities``: A list of additional abilities.
    """
    return {
        gear_path: extract_gear_stats(cast(QueryResponse, player[gear_path]))
        for gear_path in player_paths.GEARS
    }


def extract_player_data(
    player: QueryResponse, scoreboard_position: int
) -> dict[str, str | int | dict]:
    """Extracts the player data from a player's data.

    Args:
        player (QueryResponse): The player's data.
        scoreboard_position (int): The player's position on the scoreboard at
            the end of the match.

    Returns:
        dict[str, str | int | dict]: The player data. The keys are as follows:

        - ``name``: The player's name.
        - ``me``: Whether the player is the user.
        - ``player_number``: The player's number. A discriminator used to
            differentiate players with the same name.
        - ``splashtag``: The player's splashtag.
        - ``weapon``: The player's weapon ID.
        - ``inked``: The amount of turf inked.
        - ``species``: The player's species. One of ``inkling`` or ``octoling``.
        - ``scoreboard_position``: The player's position on the scoreboard at
            the end of the match.
        - ``gear``: The player's gear. See :func:`extract_gear` for details.
        - ``disconnected``: Whether the player disconnected.

        The following keys are only present if the player did not disconnect:

        - ``kills_or_assists``: The number of kills and assists, combined.
        - ``assists``: The number of assists.
        - ``kills``: The number of kills.
        - ``deaths``: The number of deaths.
        - ``specials``: The number of specials used.
        - ``signals``: The number of signals obtained.
        - ``top_500_crown``: Whether the player has a top 500 crown in the
            match.
    """
    out = {}
    out[players_keys.NAME] = player[player_paths.NAME]
    out[players_keys.ME] = player[player_paths.IS_MYSELF]
    if number := player.get(player_paths.PLAYER_NUMBER):
        out[players_keys.PLAYER_NUMBER] = str(number)

    out[players_keys.SPLASHTAG] = player[player_paths.SPLASHTAG]
    out[players_keys.WEAPON] = player[player_paths.WEAPON]
    out[players_keys.INKED] = player[player_paths.INKED]
    out[players_keys.SPECIES] = cast(str, player[player_paths.SPECIES]).lower()
    out[players_keys.SCOREBOARD_POSITION] = scoreboard_position + 1
    out[players_keys.GEAR] = extract_gear(player)

    # The following fields are empty if the player disconnected
    if player.get(player_paths.RESULT) is None:
        out[players_keys.DISCONNECTED] = True
        return out

    out[players_keys.KILLS_OR_ASSISTS] = player[player_paths.KILL_OR_ASSIST]
    out[players_keys.ASSISTS] = player[player_paths.ASSIST]
    out[players_keys.KILLS] = out[players_keys.KILLS_OR_ASSISTS] - out[players_keys.ASSISTS]
    out[players_keys.DEATHS] = player[player_paths.DEATH]
    out[players_keys.SPECIALS] = player[player_paths.SPECIAL]
    out[players_keys.SIGNALS] = player[player_paths.SIGNAL]
    out[players_keys.TOP_500_CROWN] = player[player_paths.TOP_500_CROWN]
    out[players_keys.DISCONNECTED] = False
    return out
