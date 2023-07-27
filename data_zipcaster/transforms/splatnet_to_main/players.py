from urllib.parse import urlparse

from data_zipcaster.assets import GEAR_HASHES
from data_zipcaster.models.main import players as main
from data_zipcaster.models.splatnet.submodels import players as splatnet
from data_zipcaster.utils import base64_decode


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
    sub_stats: list[main.AbilityType] = [
        extract_stat(ability.image.url) for ability in gear.additionalGearPowers
    ]
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
