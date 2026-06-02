import dataclasses

import iso8601


class ChallongeException(Exception):
    pass


def _parse(data, target_class, tz):
    if not data:
        return []
    elif isinstance(data, (tuple, list)):
        return [_parse(subdata, target_class, tz) for subdata in data]

    d = {}
    for envelope_key, inner in data.items():
        if not isinstance(inner, dict):
            raise ChallongeException(
                f"Unexpected API response: '{envelope_key}' value is {type(inner).__name__}, expected dict"
            )
        d.update(inner)

    for k, v in d.items():
        if k.endswith("_at") and isinstance(v, str):
            try:
                d[k] = iso8601.parse_date(v).astimezone(tz)
            except iso8601.ParseError:
                pass

    known = {f.name for f in dataclasses.fields(target_class)}
    return target_class(**{k: v for k, v in d.items() if k in known})


def _prepare_params(dirty_params, prefix=None):
    params = {}
    for k, v in dirty_params.items():
        v = _prepare_value(v)
        if prefix:
            params[f"{prefix}[{k}]"] = v
        else:
            params[k] = v
    return params


def _prepare_value(val):
    if hasattr(val, "isoformat"):
        return val.isoformat()
    elif isinstance(val, bool):
        return str(val).lower()
    elif isinstance(val, (tuple, list)):
        return [_prepare_value(v) for v in val]
    return val
