from data_zipcaster.importers.splatnet.paths.common import VS_HISTORY_DETAIL

# Common
KNOCKOUT = (VS_HISTORY_DETAIL, "knockout")
# Splatfest
DRAGON_MATCH = (VS_HISTORY_DETAIL, "festMatch", "dragonMatchType")
FEST_CLOUT = (VS_HISTORY_DETAIL, "festMatch", "contribution")
FEST_POWER = (VS_HISTORY_DETAIL, "festMatch", "myFestPower")
JEWEL = (VS_HISTORY_DETAIL, "festMatch", "jewel")
FEST_TEAM_NAME = "festTeamName"

# Turf War
PAINT_RATIO = (VS_HISTORY_DETAIL, "result", "paintRatio")
TRI_COLOR_ROLE = (VS_HISTORY_DETAIL, "triColorRole")

# Anarchy Open
ANARCHY_POWER = (VS_HISTORY_DETAIL, "bankaraMatch", "bankaraPower", "power")

# Challenge
CHALLENGE_POWER = (VS_HISTORY_DETAIL, "leagueMatch", "myLeaguePower")
CHALLENGE_ID = (VS_HISTORY_DETAIL, "leagueMatch", "leagueMatchEvent", "id")
