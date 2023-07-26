from typing import TypeAlias

from data_zipcaster.models.splatnet.vs import (
    AnarchyMetaData,
    ChallengeMetaData,
    TurfMetaData,
    VsDetail,
    XMetaData,
)
from data_zipcaster.models.utils import strip_prefix_keys

MetaData: TypeAlias = (
    AnarchyMetaData | XMetaData | TurfMetaData | ChallengeMetaData
)


def generate_metadata(input_dict: dict) -> MetaData:
    # Iterate through each MetaData type and try to generate it
    input_dict = strip_prefix_keys(input_dict)
    for metadata_type in [
        AnarchyMetaData,
        XMetaData,
        TurfMetaData,
        ChallengeMetaData,
    ]:
        try:
            return metadata_type(**input_dict)
        except:
            pass
    raise ValueError("Could not generate metadata")


def generate_vs_detail(input_dict: dict) -> VsDetail:
    return VsDetail(**strip_prefix_keys(input_dict))
