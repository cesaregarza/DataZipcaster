from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.common import get_teams_data
from data_zipcaster.importers.splatnet.paths import vs_modes_paths


def extract_splatfest_data(battle: QueryResponse) -> dict:
    """Extracts relevant data from a Splatfest battle and returns it as a
    dictionary.

    Args:
        battle (QueryResponse): The Splatfest battle to extract data from.

    Returns:
        dict: A dictionary containing the extracted data with the following
            keys:

            - ``clout_change``: The change in clout from the battle.
            - ``fest_power``: The Splatfest Power of the battle.
            - ``fest_dragon``: The Splatfest Dragon of the battle. This is only
                present if the battle is a Dragon (10x, 100x, or 333x) battle.
            - ``jewel``: Whether or not the player had a Splatfest Jewel
                indicating they won a Dragon battle.
            - ``our_team_theme``: The theme of the player's team.
            - ``their_team_theme``: The theme of the opposing team.
            - ``third_team_theme``: The theme of the third team. Only present
                if the battle is a Tri-Color battle.
    """
    dragon_match_type = battle[vs_modes_paths.DRAGON_MATCH]
    dragon_map = {
        "NORMAL": "1x",
        "DECUPLE": "10x",
        "DRAGON": "100x",
        "DOUBLE_DRAGON": "333x",
    }
    teams, team_keys = get_teams_data(battle)
    out = {
        "clout_change": battle[vs_modes_paths.FEST_CLOUT],
        "fest_power": battle[vs_modes_paths.FEST_POWER],
        "fest_dragon": dragon_map[dragon_match_type],
        "jewel": battle[vs_modes_paths.JEWEL],
    }
    if out["fest_dragon"] == "1x":
        out.pop("fest_dragon")

    for i, team in enumerate(teams):
        team_name = team[vs_modes_paths.FEST_TEAM_NAME[-1]]
        team_key = "%s_team_theme" % team_keys[i]
        out[team_key] = team_name

    return out


def extract_turf_war_data(battle: QueryResponse) -> dict:
    """Extracts relevant data from a Turf War battle and returns it as a
    dictionary.

    Args:
        battle (QueryResponse): The Turf War battle to extract data from.

    Returns:
        dict: A dictionary containing the extracted data with the following
            keys:

            - ``our_team_ink``: The amount of ink the player's team inked.
            - ``their_team_ink``: The amount of ink the opposing team inked.
            - ``third_team_ink``: The amount of ink the third team inked. Only
                present if the battle is a Tri-Color battle.
            - ``our_team_percent``: The percentage of the map the player's team
                inked.
            - ``their_team_percent``: The percentage of the map the opposing
                team inked.
            - ``third_team_percent``: The percentage of the map the third team
                inked. Only present if the battle is a Tri-Color battle.
            - ``our_team_role``: The role the player's team had in the battle.
                only present if the battle is a Tri-Color battle.
            - ``their_team_role``: The role the opposing team had in the
                battle. Only present if the battle is a Tri-Color battle.
            - ``third_team_role``: The role the third team had in the battle.
                Only present if the battle is a Tri-Color battle.
    """
    teams, team_keys = get_teams_data(battle)
    out = {}
    for i, team in enumerate(teams):
        try:
            team_percent_key = "%s_team_percent" % team_keys[i]
            out[team_percent_key] = (
                float(team[vs_modes_paths.PAINT_RATIO]) * 100
            )
        except KeyError:
            pass

        ink = sum(team.get_partial_path("players", ":", "paint"))
        team_ink_key = "%s_team_ink" % team_keys[i]
        out[team_ink_key] = ink

        if (role := team.get(vs_modes_paths.TRI_COLOR_ROLE)) is not None:
            role_key = "%s_team_role" % team_keys[i]
            out[role_key] = role

    return out
