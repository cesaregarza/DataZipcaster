from typing import Literal, TypeAlias

KnockoutType: TypeAlias = Literal["win", "lose", "neither"] | None
ModeType: TypeAlias = Literal[
    "regular",
    "bankara_challenge",
    "xbattle",
    "league",
    "private",
    "bankara_open",
    "splatfest_open",
    "splatfest_challenge",
    "splatfest_open",
]
RuleType: TypeAlias = Literal[
    "turf_war",
    "splat_zones",
    "tower_control",
    "rainmaker",
    "clam_blitz",
    "tricolor",
]
ResultType: TypeAlias = Literal["win", "lose", "draw", "exempted_lose"]
BadgeType: TypeAlias = tuple[str | None, str | None, str | None]
MatchMultiplierType: TypeAlias = Literal[
    "NORMAL", "DECUPLE", "DRAGON", "DOUBLE_DRAGON"
]
StackableAbilityType: TypeAlias = Literal[
    "ink_saver_main",
    "ink_saver_sub",
    "ink_recovery_up",
    "run_speed_up",
    "swim_speed_up",
    "special_charge_up",
    "special_saver",
    "special_power_up",
    "quick_respawn",
    "quick_super_jump",
    "sub_power_up",
    "ink_resistance_up",
    "sub_resistance_up",
    "intensify_action",
]
MainSlotOnlyAbilityType: TypeAlias = Literal[
    "opening_gambit",
    "last_ditch_effort",
    "tenacity",
    "comeback",
    "ninja_squid",
    "haunt",
    "thermal_ink",
    "respawn_punisher",
    "ability_doubler",
    "stealth_jump",
    "object_shredder",
    "drop_roller",
]
AbilityType: TypeAlias = MainSlotOnlyAbilityType | StackableAbilityType
SpeciesType: TypeAlias = Literal["inkling", "octoling"]
CrownType: TypeAlias = Literal["DRAGON", "DOUBLE_DRAGON"]
