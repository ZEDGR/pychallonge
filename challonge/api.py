import json
import iso8601
import tzlocal
import pytz
from httpx import request
from httpx import HTTPStatusError

tz = tzlocal.get_localzone()

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


def set_timezone(new_tz=None):
    """Set the timezone for datetime fields.
    By default is your machine's time.
    If it's called without parameter sets the
    local time again.

    Args:
        new_tz (str, optional): timezone string. Defaults to None.
            ex. 'Europe/Athens',
                'Asia/Seoul',
                'America/Los_Angeles',
                'UTC'
    """
    global tz
    if new_tz:
        tz = pytz.timezone(new_tz)
    else:
        tz = tzlocal.get_localzone()


def get_credentials():
    """Retrieve the challonge.com credentials set with set_credentials().

    Returns:
        A tuple with user and API key
    """
    return _credentials["user"], _credentials["api_key"]


def get_timezone():
    """Return currently timezone in use.

    Returns:
        A timezone object
    """
    return tz


def fetch(method, uri, params_prefix=None, timeout=30.0, **params):
    """Fetch the given uri and return the contents of the response.

    Args:
        method (str): The HTTP method for the API request (GET, POST, PUT, DELETE)
        uri (str): The URI of the API endpoint
        params_prefix (str, optional): It is one of the "name", "url", "tournament_type". Defaults to None.
        timeout (float, optional): The timeout of the request in seconds. Defaults to 30.0 seconds
        params (list, optional): The parameters of the tournament

    Returns:
        A str representing the json response
    """
    p_params = _prepare_params(params, params_prefix)
    if method == "POST" or method == "PUT":
        r_data = {"data": p_params}
    else:
        r_data = {"params": p_params}

    # build the HTTP request and use basic authentication
    url = "https://%s/%s.json" % (CHALLONGE_API_URL, uri)

    try:
        response = request(
            method,
            url,
            auth=get_credentials(),
            timeout=timeout,
            **r_data
        )
        response.raise_for_status()
    except HTTPStatusError as e:
        if e.response.status_code != 422:
            e.response.raise_for_status()
        # wrap up application-level errors
        doc = e.response.json()
        if doc.get("errors"):
            raise ChallongeException(*doc['errors'])

    return response


def fetch_and_parse(method, uri, params_prefix=None, timeout=30.0, **params):
    """Fetch the given uri and return python dictionary with parsed data-types.

    Args:
        method (str): The HTTP method for the API request (GET, POST, PUT, DELETE)
        uri (str): The URI of the API endpoint
        params_prefix (str, optional): It is one of the "name", "url", "tournament_type". Defaults to None.
        timeout (float, optional): The timeout of the request in seconds. Defaults to 30.0 seconds
        params (list, optional): The parameters of the tournament

    Returns:
        A dict representing the json response
    """
    response = fetch(method, uri, params_prefix, timeout, **params)
    return _parse(json.loads(response.text))


def _parse(data):
    """Recursively convert a json into python data types.

    Args:
        data (dict): The dict with the response

    Returns:
        A dict with the values converted to appropriate python data types
    """
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
            "challonge_username"
        }:
            continue  # do not test type of fields which are always strings
        if isinstance(v, str):
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

    Args:
        dirty_params (dict): The parameters given for the API request
        prefix (str, optional): Defaults to None.

    Note:
        The `prefix` can be used to convert parameters with keys that
        look like ("name", "url", "tournament_type") into something like
        ("tournament[name]", "tournament[url]", "tournament[tournament_type]"),
        which is how challonge.com expects parameters describing specific
        objects.

    Returns:
        A list of parameters in format ready to use for the API request

    """
    params = {}
    for k, v in dirty_params.items():
        v = _prepare_value(v)
        if prefix:
            params[f"{prefix}[{k}]"] = v
        else:
            params[k] = v
    return params


def _prepare_value(val):
    """Change value format to be accepted by challonge.com API. This function is used by _prepare_params.

    Args:
        val (obj): values from prepare_params (int, str, bool, datetime, etc)

    Returns:
        The value in a correct format (lowercase for str for bool values and isoformat for the datetime objects)
    """
    prepared_val = None
    if hasattr(val, "isoformat"):
        prepared_val = val.isoformat()
    elif isinstance(val, bool):
        # challonge.com only accepts lowercase true/false
        prepared_val = str(val).lower()
    elif isinstance(val, (tuple, list)):
        prepared_val = []
        for v in val:
            prepared_val.append(_prepare_value(v))
    else:
        prepared_val = val

    return prepared_val
