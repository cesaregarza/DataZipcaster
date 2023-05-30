from splatnet3_scraper.query import QueryResponse

from data_zipcaster.importers.splatnet.extractors.common import get_teams_data
from data_zipcaster.importers.splatnet.paths import vs_modes_paths


def extract_splatfest_data(battle: QueryResponse) -> dict:
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
