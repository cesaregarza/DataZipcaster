def delete_none_keys(dict_: dict) -> dict:
    keys = list(dict_.keys())
    for key in keys:
        if dict_[key] is None:
            del dict_[key]

    return dict_
