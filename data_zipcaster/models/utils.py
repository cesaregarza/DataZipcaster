def strip_prefix_keys(obj: dict, old_key_prefix: str = "__") -> dict:
    """Recursively strip a prefix from all keys in a recursive dict that is
    structured like a JSON object.

    Args:
        obj (dict): The dict to strip the prefix from.
        old_key_prefix (str): The prefix to strip. Defaults to "__".

    Returns:
        dict: The dict with the prefix stripped.
    """
    if isinstance(obj, dict):
        return {
            k.replace(old_key_prefix, ""): strip_prefix_keys(v, old_key_prefix)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [strip_prefix_keys(v, old_key_prefix) for v in obj]
    else:
        return obj
