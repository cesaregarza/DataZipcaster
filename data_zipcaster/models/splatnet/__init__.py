from typing import TypeAlias

from pydantic import ValidationError

from data_zipcaster.models.splatnet.submodels import (
    AwardRankType,
    Background,
    Badge,
    BankaraMatch,
    BankaraMatchChallenge,
    Brand,
    Color,
    CrownType,
    Gear,
    GearPower,
    GroupNodeItems,
    HGBankaraMatch,
    HGFGroupNodeItem,
    HGFHistoryDetails,
    HGFNodeItem,
    HGFPlayer,
    HGFSpecialWeapon,
    HGFWeapon,
    HistoryDetails,
    HistoryGroupOnlyFirst,
    HistoryGroups,
    KnockoutType,
    LeagueMatch,
    LeagueMatchEvent,
    LeagueMatchHistoryGroup,
    MaskingImage,
    MatchMultiplierType,
    MyTeam,
    MyTeamResult,
    Nameplate,
    NodeItems,
    OneHistoryDetail,
    Player,
    PlayerHistoryGroup,
    PlayerResult,
    PlayerRoot,
    ResultType,
    RuleType,
    SpecialWeapon,
    SpeciesType,
    SplatfestMatch,
    SubWeapon,
    Summary,
    Team,
    TeamResult,
    TricolorRoleType,
    Url,
    UsualGearPower,
    VsMode,
    VsRule,
    VsStage,
    Weapon,
    WeaponHistoryGroup,
    XMatch,
    XMatchMeasurement,
    XPower,
)
from data_zipcaster.models.splatnet.vs import (
    AnarchyMetadata,
    ChallengeMetadata,
    TurfMetadata,
    VsDetail,
    XMetadata,
)
from data_zipcaster.models.utils import strip_prefix_keys

Metadata: TypeAlias = (
    AnarchyMetadata | XMetadata | TurfMetadata | ChallengeMetadata
)


def generate_metadata(input_dict: dict) -> Metadata:
    # Iterate through each Metadata type and try to generate it
    input_dict = strip_prefix_keys(input_dict)
    for metadata_type in [
        AnarchyMetadata,
        XMetadata,
        TurfMetadata,
        ChallengeMetadata,
    ]:
        try:
            return metadata_type(**input_dict)
        except ValidationError:
            pass
    raise ValueError("Could not generate metadata")


def generate_vs_detail(input_dict: dict) -> VsDetail:
    return VsDetail(**strip_prefix_keys(input_dict))
