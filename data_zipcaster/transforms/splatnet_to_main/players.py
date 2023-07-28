from typing import cast
from urllib.parse import urlparse

from data_zipcaster.assets import GEAR_HASHES
from data_zipcaster.models import main, splatnet
from data_zipcaster.utils import base64_decode, color_from_percent_to_str


def convert_weapon_id(player: splatnet.Player) -> int:
    weapon_id = base64_decode(player.weapon.id)[len("Weapon-") :]
    return int(weapon_id)


def convert_gear_stats(gear: splatnet.Gear) -> main.GearItem:
    def extract_stat(url: str) -> main.AbilityType:
        path = urlparse(url).path
        hash = path.split("/")[-1][:64]
        return GEAR_HASHES[hash]

    gear_name = gear.name
    brand_name = gear.brand.name
    main_stat = extract_stat(gear.primaryGearPower.image.url)
    sub_stats: list[main.StackableAbilityType] = [
        cast(main.StackableAbilityType, extract_stat(ability.image.url))
        for ability in gear.additionalGearPowers
    ]
    sub_stats = (sub_stats + [None] * 3)[:3]
    return main.GearItem(
        name=gear_name,
        brand=brand_name,
        primary_ability=main_stat,
        additional_abilities=sub_stats,
    )


def convert_gear(player: splatnet.Player) -> main.Gear:
    headgear = convert_gear_stats(player.headGear)
    clothing = convert_gear_stats(player.clothingGear)
    shoes = convert_gear_stats(player.shoesGear)
    return main.Gear(
        headgear=headgear,
        clothing=clothing,
        shoes=shoes,
    )


def convert_species(species: splatnet.SpeciesType) -> main.SpeciesType:
    species_remap: dict[splatnet.SpeciesType, main.SpeciesType] = {
        "INKLING": "inkling",
        "OCTOLING": "octoling",
    }
    return species_remap[species]


def convert_nameplate(player: splatnet.Player) -> main.Nameplate:
    badges: list[str | None] = [None, None, None]
    for i, badge in enumerate(player.nameplate.badges):
        if badge is None:
            continue
        badges[i] = base64_decode(badge.id)[len("Badge-") :]

    badges_out = cast(main.BadgeType, badges)
    text_color = color_from_percent_to_str(
        player.nameplate.background.textColor.model_dump()
    )
    background_id = base64_decode(player.nameplate.background.id)
    return main.Nameplate(
        badges=badges_out,
        text_color=text_color,
        background_id=background_id[len("NameplateBackground-") :],
    )


def convert_crown_type(crown_type: splatnet.CrownType) -> main.CrownType | None:
    if crown_type == "NONE":
        return None
    crown_remap: dict[splatnet.CrownType, main.CrownType] = {
        "DRAGON": "dragon",
        "DOUBLE_DRAGON": "double_dragon",
    }
    return crown_remap[crown_type]


def convert_player(
    player: splatnet.Player, scoreboard_position: int
) -> main.Player:
    player_id = base64_decode(player.id).split(":")[-1]
    out = main.Player(
        name=player.name,
        npln_id=player_id,
        me=player.isMyself,
        splashtag=player.byname,
        nameplate=convert_nameplate(player),
        weapon_name=player.weapon.name,
        weapon_id=convert_weapon_id(player),
        sub_name=player.weapon.subWeapon.name,
        special_name=player.weapon.specialWeapon.name,
        inked=player.paint,
        species=convert_species(player.species),
        scoreboard_position=scoreboard_position,
        gear=convert_gear(player),
        disconnected=(player.result is None),
    )

    # First vs game will not have a player number
    if number := player.nameId:
        out.player_number = str(number)

    if player.result is not None:
        out.kills_or_assists = player.result.kill
        out.assists = player.result.assist
        out.kills = player.result.kill - player.result.assist
        out.deaths = player.result.death
        out.specials = player.result.special
        out.signals = player.result.noroshiTry
        out.crown = player.crown

    if (crown_type := player.festDragonCert) is not None and (
        crown_type != "NONE"
    ):
        out.crown_type = convert_crown_type(crown_type)
        out.crown = True

    return out
