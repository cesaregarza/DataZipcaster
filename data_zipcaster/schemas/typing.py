from typing import Literal, TypeAlias

KnockoutType: TypeAlias = Literal["win", "lose", "neither"] | None
ModeType: TypeAlias = Literal[
    "regular",
    "bankara_challenge",
    "xbattle",
    "league",
    "private",
    "bankara-open",
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
