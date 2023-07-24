import datetime as dt

from data_zipcaster.exporters.splashcat.utils import delete_none_keys
from data_zipcaster.schemas.players import GearItemDict, PlayerDict
from data_zipcaster.schemas.typing import ModeType
from data_zipcaster.schemas.vs_modes import (
    SplatfestMetadataDict,
    TeamDict,
    VsExtractDict,
)
from data_zipcaster.utils import color_from_str_to_percent

MODE_MAP = {
    "regular": "REGULAR",
    "bankara_challenge": "BANKARA",
    "bankara_open": "BANKARA",
    "xbattle": "X_MATCH",
    "splatfest_open": "FEST",
    "splatfest_challenge": "FEST",
    "private": "PRIVATE",
    "league": "CHALLENGE",
}

RULE_MAP = {
    "splat_zones": "AREA",
    "tower_control": "LOFT",
    "tricolor": "TRI_COLOR",
    "turf_war": "TURF_WAR",
    "rainmaker": "GOAL",
    "clam_blitz": "CLAM",
}

MULT_MAP = {
    1: "NONE",
    10: "DECUPLE",
    100: "DRAGON",
    333: "DOUBLE_DRAGON",
}


def convert_id(id: str) -> str:
    return id.split(":")[-1]


def convert_start_time(start_time: float) -> str:
    return dt.datetime.fromtimestamp(start_time).isoformat()


def convert_splatfest(extract: VsExtractDict) -> dict:
    mult = extract["splatfest_metadata"]["match_multiplier"]
    power = extract.get("match_power", None)
    out = {
        "mode": "PRO" if "pro" in extract["mode"] else "OPEN",
        "cloutMultiplier": MULT_MAP[mult],
    }
    if power is not None:
        out["power"] = power
    return out


def convert_anarchy(extract: VsExtractDict) -> dict:
    series_metadata = extract.get("series_metadata", None)
    power = extract.get("match_power", None)
    point_change = series_metadata.get("rank_exp_change", None)
    s_plus_number = series_metadata.get("rank_after_s_plus", None)

    out = {
        "mode": "OPEN" if "open" in extract["mode"] else "SERIES",
        "rank": series_metadata["rank_after"],
    }
    if power is not None:
        out["power"] = power

    if point_change is not None:
        out["pointChange"] = point_change

    if s_plus_number is not None:
        out["sPlusNumber"] = s_plus_number

    return out


def convert_xbattles(extract: VsExtractDict) -> dict:
    series_metadata = extract.get("series_metadata", None)
    power = extract.get("match_power", None)
    rank = series_metadata.get("rank_estimate", None)
    out = {}
    if power is not None:
        out["xPower"] = power

    if rank is not None:
        out["xRank"] = rank

    return out


def convert_challenge(extract: VsExtractDict) -> dict:
    power = extract.get("match_power", None)

    out = {
        "id": extract["challenge_id"],
    }
    if power is not None:
        out["power"] = power

    return out


def convert_team(team: TeamDict, player_team: bool) -> dict:
    out = {
        "isMyTeam": player_team,
        "color": color_from_str_to_percent(team["color"]),
        "order": team["order"],
    }
    if (result := team.get("result", None)) is not None:
        out["score"] = result.get("score", None)
        out["noroshi"] = result.get("noroshi", None)
        out["paintRatio"] = result.get("paint_ratio", None)
        out["judgement"] = result["team_result"].upper()

    if (splatfest := team.get("splatfest", None)) is not None:
        out["festTeamName"] = splatfest.get("team_name", None)
        out["festUniformBonusRate"] = splatfest.get("synergy_bonus", None)
        out["festUniformName"] = splatfest.get("synergy_name", None)
        out["tricolorRole"] = splatfest.get("tricolor_role", None)

    out = delete_none_keys(out)

    out["players"] = [convert_player(player) for player in team["players"]]
    return out


def convert_player(player: PlayerDict) -> dict:
    # Required
    out = {
        "isMe": player["me"],
        "disconnected": player["disconnected"],
        "species": player["species"].upper(),
        "nplnId": player["npln_id"],
        "name": player["name"],
        "nameId": player.get("player_number", None),
        "title": player["splashtag"],
        "splashtagBackgroundId": int(player["nameplate"]["background_id"]),
        "weaponId": player["weapon_id"],
        "paint": player["inked"],
        "headGear": convert_gear(player["gear"]["headgear"]),
        "clothingGear": convert_gear(player["gear"]["clothing"]),
        "shoesGear": convert_gear(player["gear"]["shoes"]),
    }
    out["badges"] = [
        int(badge) if badge is not None else None
        for badge in player["nameplate"]["badges"]
    ]

    # Not required
    if not out["disconnected"]:
        out["kills"] = player.get("kills_or_assists", None)
        out["assists"] = player.get("assists", None)
        out["deaths"] = player.get("deaths", None)
        out["specials"] = player.get("specials", None)
        out["noroshiTry"] = player.get("signals", None)

    return delete_none_keys(out)


ABILITY_MAP = {
    "ink_saver_main": "Ink Saver (Main)",
    "ink_saver_sub": "Ink Saver (Sub)",
    "ink_recovery_up": "Ink Recovery Up",
    "run_speed_up": "Run Speed Up",
    "swim_speed_up": "Swim Speed Up",
    "special_charge_up": "Special Charge Up",
    "special_saver": "Special Saver",
    "special_power_up": "Special Power Up",
    "quick_respawn": "Quick Respawn",
    "quick_super_jump": "Quick Super Jump",
    "sub_power_up": "Sub Power Up",
    "ink_resistance_up": "Ink Resistance Up",
    "sub_resistance_up": "Sub Resistance Up",
    "intensify_action": "Intensify Action",
    "opening_gambit": "Opening Gambit",
    "last_ditch_effort": "Last-Ditch Effort",
    "tenacity": "Tenacity",
    "comeback": "Comeback",
    "ninja_squid": "Ninja Squid",
    "haunt": "Haunt",
    "thermal_ink": "Thermal Ink",
    "respawn_punisher": "Respawn Punisher",
    "ability_doubler": "Ability Doubler",
    "stealth_jump": "Stealth Jump",
    "object_shredder": "Object Shredder",
    "drop_roller": "Drop Roller",
}


def convert_gear(gear: GearItemDict) -> dict:
    out = {
        "name": gear["name"],
        "primaryAbility": ABILITY_MAP[gear["primary_ability"]],
        "secondaryAbilities": [
            ABILITY_MAP.get(ability, None)
            for ability in gear["additional_abilities"]
        ],
    }
    out["secondaryAbilities"] = [
        ability if ability else "Unknown" for ability in out["secondaryAbilities"]
    ]

    return out


def convert(extract: VsExtractDict) -> dict:
    out = {
        "splatnetId": convert_id(extract["id"]),
        "vsMode": MODE_MAP[extract["mode"]],
        "vsRule": RULE_MAP[extract["rule"]],
        "vsStageId": int(extract["stage"]),
        "playedTime": convert_start_time(extract["start_time"]),
        "duration": extract["duration"],
        "judgement": extract["result"].upper(),
        "knockout": extract["knockout"],
        "awards": [medal["name"] for medal in extract["medals"]],
    }
    teams = extract["teams"]
    # Iterate over the teams and find the player's team
    team_idx = None
    for team in teams:
        for player in team["players"]:
            if player["me"]:
                team_idx = team["order"] - 1
                break
        if team_idx is not None:
            break

    out["teams"] = [
        convert_team(team, i == team_idx) for i, team in enumerate(teams)
    ]

    if extract["mode"] in ["splatfest_open", "splatfest_challenge"]:
        out["splatfest"] = convert_splatfest(extract)
    elif extract["mode"] == "league":
        out["challenge"] = convert_challenge(extract)
    elif extract["mode"] == "xbattle":
        out["xBattle"] = convert_xbattles(extract)
    elif extract["mode"] in ["bankara_challenge", "bankara_open"]:
        out["anarchy"] = convert_anarchy(extract)

    return delete_none_keys(out)
