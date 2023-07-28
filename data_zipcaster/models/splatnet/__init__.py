from typing import TypeAlias

from data_zipcaster.models.splatnet.submodels import *
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
        except:
            pass
    raise ValueError("Could not generate metadata")


def generate_vs_detail(input_dict: dict) -> VsDetail:
    return VsDetail(**strip_prefix_keys(input_dict))
