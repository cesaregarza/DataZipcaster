import base64
import re
from typing import Any, cast

from splatnet3_scraper.query import QueryResponse

rank_re = re.compile(r"^([cbas][+-]?)(\d{1,2})?$")


def base64_decode(data: str) -> str:
    """Decodes a base64 string into utf-8 string.

    Args:
        data (str): The base64 string to decode. Generally this should be any of
            the ``id`` fields in the battle data.

    Returns:
        str: The decoded string.
    """
    return base64.b64decode(data).decode("utf-8")


def color_from_percent_to_str(color_dict: dict | QueryResponse) -> str:
    """Converts a color from a percent to a string.

    Args:
        color_dict (dict): The color dictionary. This should be a dictionary
            with the keys ``r``, ``g``, and ``b``. The values of these keys
            should be integers from 0 to 255.

    Returns:
        str: The color as a string. This will be in the format ``#RRGGBB``.
    """

    if isinstance(color_dict, QueryResponse):
        color_dict = cast(dict, color_dict.data)

    def color_to_str(color: float) -> str:
        return f"{int(color * 255):02x}"

    return "".join([color_to_str(color_dict[color]) for color in "rgba"])


def color_from_str_to_percent(color_str: str) -> dict[str, float]:
    """Converts a color from a string to a percent.

    Args:
        color_str (str): The color string. This should be a string in the format
            ``#RRGGBB``.

    Returns:
        dict[str, float]: The color as a dictionary. This will have the keys
            ``r``, ``g``, and ``b``. The values of these keys will be floats
            from 0 to 1.
    """
    if color_str.startswith("#"):
        color_str = color_str[1:]
    return {
        "r": int(color_str[0:2], 16) / 255,
        "g": int(color_str[2:4], 16) / 255,
        "b": int(color_str[4:6], 16) / 255,
        "a": int(color_str[6:8], 16) / 255 if len(color_str) > 6 else 1.0,
    }


def parse_rank(rank: str) -> tuple[str, int | None]:
    """Parses a rank string.

    Args:
        rank (str): The rank string to parse.

    Raises:
        ValueError: If the rank string is invalid.

    Returns:
        tuple[str, str | None]: The parsed rank. The first element is the rank,
            so it will be one of ``c``, ``b``, ``a``, or ``s`` with an optional
            ``+`` or ``-``. The second element is the S+ rank, which will be
            ``None`` if the rank is not ``S+``. Otherwise, it will be a string
            containing the ``S+`` rank value, which will be a number from 0 to
            50.
    """
    rank = rank.lower()
    match = rank_re.match(rank)
    if match is None:
        raise ValueError(f"Invalid rank string: {rank}")
    groups = match.groups()
    rank_val = groups[0]
    s_rank_val = cast(str | int | None, groups[1])
    if s_rank_val is not None and isinstance(s_rank_val, str):
        s_rank_val = int(s_rank_val)

    return cast(tuple[str, int | None], (rank_val, s_rank_val))


def cast_qr(item: Any) -> QueryResponse:
    return cast(QueryResponse, item)
