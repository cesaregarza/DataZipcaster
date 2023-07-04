from data_zipcaster.importers.splatnet.extractors.vs_battles import (
    build_vs_extract,
    extract_anarchy,
    extract_xbattle,
)

EXTRACT_MAP = {
    "xbattle": extract_xbattle,
    "anarchy": extract_anarchy,
    "turf": build_vs_extract,
    "private": build_vs_extract,
    "challenge": build_vs_extract,
}
