import datetime as dt

from data_zipcaster.models import main
from data_zipcaster.utils import color_from_str_to_percent, delete_none_keys

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


MULT_MAP = {
    1: "NONE",
    10: "DECUPLE",
    100: "DRAGON",
    333: "DOUBLE_DRAGON",
}

RULE_MAP = {
    "splat_zones": "AREA",
    "tower_control": "LOFT",
    "tricolor": "TRI_COLOR",
    "turf_war": "TURF_WAR",
    "rainmaker": "GOAL",
    "clam_blitz": "CLAM",
}


def convert_id(id: str) -> str:
    return id.split(":")[-1]


def convert_start_time(start_time: dt.datetime) -> str:
    return start_time.isoformat()


def convert_duration(duration: dt.timedelta) -> float:
    return int(duration.total_seconds())


def convert_splatfest(model: main.VsExtract) -> dict:
    assert model.splatfest_metadata is not None
    mult = model.splatfest_metadata.match_multiplier
    power = model.match_power
    out: dict = {
        "mode": "PRO" if "pro" in model.mode else "OPEN",
        "cloutMultiplier": MULT_MAP[mult],
    }
    if power is not None:
        out["power"] = power
    return out


def convert_anarchy(model: main.VsExtract) -> dict:
    assert isinstance(model.series_metadata, main.AnarchyMetadata)
    out: dict = {
        "mode": "OPEN" if model.mode == "bankara_open" else "SERIES",
    }

    if model.series_metadata.rank_after is not None:
        out["rank"] = model.series_metadata.rank_after.upper()

    if model.match_power is not None:
        out["power"] = model.match_power

    if model.series_metadata.rank_exp_change is not None:
        out["pointChange"] = model.series_metadata.rank_exp_change

    if model.series_metadata.rank_after_s_plus is not None:
        out["sPlusNumber"] = model.series_metadata.rank_after_s_plus

    return out


def convert_xbattles(model: main.VsExtract) -> dict:
    assert isinstance(model.series_metadata, main.XMetadata)
    out = {}
    if model.match_power is not None:
        out["xPower"] = model.match_power

    if model.series_metadata.rank_estimate is not None:
        out["xRank"] = model.series_metadata.rank_estimate

    return out


def convert_challenge(model: main.VsExtract) -> dict:
    out: dict = {"id": model.challenge_id}
    if model.match_power is not None:
        out["power"] = model.match_power

    return out


def convert_team(team: main.Team, player_team: bool) -> dict:
    out = {
        "isMyTeam": player_team,
        "color": color_from_str_to_percent(team.color),
        "order": team.order,
    }

    if team.result is not None:
        out["score"] = team.result.score
        out["noroshi"] = team.result.noroshi
        out["paintRatio"] = team.result.paint_ratio
        out["judgement"] = team.result.team_result.upper()

    if team.splatfest is not None:
        out["festTeamName"] = team.splatfest.team_name
        out["festUniformBonusRate"] = team.splatfest.synergy_bonus
        out["festUniformName"] = team.splatfest.synergy_name
        out["tricolorRole"] = team.splatfest.tricolor_role

    out = delete_none_keys(out)
    out["players"] = [convert_player(player) for player in team.players]
    return out


def convert_player(player: main.Player) -> dict:
    out = {
        "isMe": player.me,
        "disconnected": player.disconnected,
        "species": player.species.upper(),
        "nplnId": player.npln_id,
        "name": player.name,
        "nameId": player.player_number,
        "title": player.splashtag,
        "paint": player.inked,
        "splashtagBackgroundId": int(player.nameplate.background_id),
        "weaponId": player.weapon_id,
        "headGear": convert_gear(player.gear.headgear),
        "clothingGear": convert_gear(player.gear.clothing),
        "shoesGear": convert_gear(player.gear.shoes),
    }
    out["badges"] = [
        int(badge) if badge is not None else None
        for badge in player.nameplate.badges
    ]

    if not player.disconnected:
        out["kills"] = player.kills_or_assists
        out["assists"] = player.assists
        out["deaths"] = player.deaths
        out["specials"] = player.specials
        out["noroshiTry"] = player.signals

    return delete_none_keys(out)


def convert_gear(gear: main.GearItem) -> dict:
    out = {
        "name": gear.name,
        "primaryAbility": ABILITY_MAP[str(gear.primary_ability)],
        "secondaryAbilities": [
            ABILITY_MAP.get(str(ability), "Unknown")
            for ability in gear.additional_abilities
        ],
    }
    return out


def find_player_team(teams: list[main.Team]) -> int:
    for team in teams:
        for player in team.players:
            if player.me:
                return team.order - 1

    return -1  # Should never happen but mypy complains otherwise


def generate_view(model: main.VsExtract) -> dict:
    out = {
        "splatnetId": convert_id(model.id),
        "vsMode": MODE_MAP[model.mode],
        "vsRule": RULE_MAP[model.rule],
        "vsStageId": int(model.stage),
        "playedTime": convert_start_time(model.start_time),
        "duration": convert_duration(model.duration),
        "judgement": model.result.upper(),
        "awards": [award.name for award in model.awards],
    }
    team_idx = find_player_team(model.teams)

    out["teams"] = [
        convert_team(team, team_idx == idx)
        for idx, team in enumerate(model.teams)
    ]

    if model.knockout is not None:
        out["knockout"] = model.knockout.upper()

    if model.mode in ("splatfest_open", "splatfest_challenge"):
        out["splatfest"] = convert_splatfest(model)
    elif model.mode == "league":
        out["challenge"] = convert_challenge(model)
    elif model.mode == "xbattle":
        out["xBattle"] = convert_xbattles(model)
    elif model.mode in ("bankara_challenge", "bankara_open"):
        out["anarchy"] = convert_anarchy(model)

    return delete_none_keys(out)
