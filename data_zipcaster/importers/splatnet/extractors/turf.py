from typing import cast

from splatnet3_scraper.query import QueryResponse

from data_zipcaster.constants import MATCH_MULTIPLIERS
from data_zipcaster.importers.splatnet.paths import vs_modes_paths
from data_zipcaster.schemas.typing import MatchMultiplierType
from data_zipcaster.schemas.vs_modes import SplatfestMetadataDict


def extract_splatfest_data(battle: QueryResponse) -> SplatfestMetadataDict:
    """Extracts relevant data from a Splatfest battle and returns it as a
    dictionary.

    Args:
        battle (QueryResponse): The Splatfest battle to extract data from.

    Returns:
        SplatfestMetadataDict: A dictionary containing the extracted data with
            the following keys:

            - ``clout``: The amount of clout the player earned.
            - ``match_multiplier``: The match multiplier for the battle. This
                    is 1, 10, 100, or 333.
            - ``jewel``: Whether the player obtained a crown, known as a jewel.
    """
    match_multiplier_type = cast(
        MatchMultiplierType, battle[vs_modes_paths.DRAGON_MATCH]
    )
    clout = cast(int, battle[vs_modes_paths.FEST_CLOUT])
    jewel = cast(int, battle[vs_modes_paths.JEWEL])

    return SplatfestMetadataDict(
        clout=clout,
        match_multiplier=MATCH_MULTIPLIERS[match_multiplier_type],
        jewel=jewel,
    )
