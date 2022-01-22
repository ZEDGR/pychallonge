import json
import iso8601
import tzlocal
import pytz
import itertools
import sys
from requests import request
from requests.exceptions import HTTPError

PY2 = sys.version_info[0] == 2
TEXT_TYPE = unicode if PY2 else str
tz = tzlocal.get_localzone()
user_agent = "pychallonge-1.11.5"

CHALLONGE_API_URL = "api.challonge.com/v1"

_credentials = {
    "user": None,
    "api_key": None,
}


class ChallongeException(Exception):
    pass


def set_credentials(username, api_key):
    """Set the challonge.com api credentials to use."""
    _credentials["user"] = username
    _credentials["api_key"] = api_key


def set_user_agent(agent):
    """Set User-Agent in the HTTP requests.

    :keyword param agent: string
    ex. 'test agent 1'
    """
    global user_agent
    user_agent = agent


def set_timezone(new_tz=None):
    """Set the timezone for datetime fields.
    By default is your machine's time.
    If it's called without parameter sets the
    local time again.

    :keyword param new_tz: timezone string
    ex. 'Europe/Athens',
        'Asia/Seoul',
        'America/Los_Angeles',
        'UTC'

    :return
        None
    """
    global tz
    if new_tz:
        tz = pytz.timezone(new_tz)
    else:
        tz = tzlocal.get_localzone()


def get_credentials():
    """Retrieve the challonge.com credentials set with set_credentials()."""
    return _credentials["user"], _credentials["api_key"]


def get_timezone():
    """Return currently timezone in use."""
    return tz


def fetch(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return the contents of the response."""
    params = _prepare_params(params, params_prefix)

    if method == "POST" or method == "PUT":
        r_data = {"data": params}
    else:
        r_data = {"params": params}

    # build the HTTP request and use basic authentication
    url = "https://%s/%s.json" % (CHALLONGE_API_URL, uri)

    try:
        response = request(
            method, url, headers={"User-Agent": user_agent}, auth=get_credentials(), **r_data
        )
        response.raise_for_status()
    except HTTPError:
        if response.status_code != 422:
            response.raise_for_status()
        # wrap up application-level errors
        doc = response.json()
        if doc.get("errors"):
            raise ChallongeException(*doc["errors"])

    return response


def fetch_and_parse(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return python dictionary with parsed data-types."""
    response = fetch(method, uri, params_prefix, **params)
    return _parse(json.loads(response.text))


def _parse(data):
    """Recursively convert a json into python data types"""

    if not data:
        return []
    elif isinstance(data, (tuple, list)):
        return [_parse(subdata) for subdata in data]

    # extract the nested dict. ex. {"tournament": {"url": "7k1safq" ...}}
    d = {ik: v for k in data.keys() for ik, v in data[k].items()}

    # convert datetime strings to datetime objects
    # and float number strings to float
    to_parse = dict(d)
    for k, v in to_parse.items():
        if k in {
            "name",
            "display_name",
            "display_name_with_invitation_email_address",
            "username",
            "challonge_username",
            "misc",
        }:
            continue  # do not test type of fields which are always strings
        if isinstance(v, TEXT_TYPE):
            try:
                dt = iso8601.parse_date(v)
                d[k] = dt.astimezone(tz)
            except iso8601.ParseError:
                try:
                    d[k] = float(v)
                except ValueError:
                    pass

    return d


def _prepare_params(dirty_params, prefix=None):
    """Prepares parameters to be sent to challonge.com.

    The `prefix` can be used to convert parameters with keys that
    look like ("name", "url", "tournament_type") into something like
    ("tournament[name]", "tournament[url]", "tournament[tournament_type]"),
    which is how challonge.com expects parameters describing specific
    objects.

    """
    if prefix and prefix.endswith("[]"):
        keys = []
        values = []
        for k, v in dirty_params.items():
            if isinstance(v, (tuple, list)):
                keys.append(k)
                values.append(v)
        firstiter = ((k, v) for vals in zip(*values) for k, v in zip(keys, vals))
        lastiter = ((k, v) for k, v in dirty_params.items() if k not in keys)
        dpiter = itertools.chain(firstiter, lastiter)
    else:
        dpiter = dirty_params.items()

    params = []
    for k, v in dpiter:
        if isinstance(v, (tuple, list)):
            for val in v:
                val = _prepare_value(val)
                if prefix:
                    params.append(("%s[%s][]" % (prefix, k), val))
                else:
                    params.append((k + "[]", val))
        else:
            v = _prepare_value(v)
            if prefix:
                params.append(("%s[%s]" % (prefix, k), v))
            else:
                params.append((k, v))

    return params


def _prepare_value(val):
    if hasattr(val, "isoformat"):
        val = val.isoformat()
    elif isinstance(val, bool):
        # challonge.com only accepts lowercase true/false
        val = str(val).lower()
    return val
