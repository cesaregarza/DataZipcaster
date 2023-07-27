from typing import Literal, TypeAlias

KnockoutType: TypeAlias = Literal["WIN", "LOSE", "NEITHER"]
RuleType: TypeAlias = Literal[
    "TURF_WAR",
    "AREA",
    "LOFT",
    "GOAL",
    "CLAM",
    "TRICOLOR",
]
ResultType: TypeAlias = Literal[
    "WIN", "LOSE", "DRAW", "EXEMPTED_LOSE", "DEEMED_LOSE"
]
AwardRankType: TypeAlias = Literal["GOLD", "SILVER"]

MatchMultiplierType: TypeAlias = Literal[
    "NORMAL", "DECUPLE", "DRAGON", "DOUBLE_DRAGON"
]
TricolorRoleType: TypeAlias = Literal["DEFENSE", "ATTACK1", "ATTACK2"]
SpeciesType: TypeAlias = Literal["INKLING", "OCTOLING"]
