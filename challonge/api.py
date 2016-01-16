import decimal
import iso8601
import itertools
from requests import request
from requests.exceptions import HTTPError

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree


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


def get_credentials():
    """Retrieve the challonge.com credentials set with set_credentials()."""
    return _credentials["user"], _credentials["api_key"]


def fetch(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return the contents of the response."""
    params = _prepare_params(params, params_prefix)

    # build the HTTP request and use basic authentication
    url = "https://%s/%s.xml" % (CHALLONGE_API_URL, uri)

    try:
        response = request(
            method,
            url,
            params=params,
            auth=get_credentials())
        response.raise_for_status()
    except HTTPError:
        if response.status_code != 422:
            raise
        # wrap up application-level errors
        doc = ElementTree.fromstring(response.text)
        if doc.tag != "errors":
            raise
        errors = [e.text for e in doc]
        raise ChallongeException(*errors)

    # use of encode() function to remove non-breaking spaces
    # with non-breaking spaces the XML parser fails in Python2
    return response.text.encode('UTF-8')


def fetch_and_parse(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return the root Element of the response."""
    doc = ElementTree.fromstring(fetch(method, uri, params_prefix, **params))
    return _parse(doc)


def _parse(root):
    """Recursively convert an Element into python data types"""
    if root.tag == "nil-classes":
        return []
    elif root.get("type") == "array":
        return [_parse(child) for child in root]

    d = {}
    for child in root:
        type = child.get("type") or "string"

        if child.get("nil"):
            value = None
        elif type == "boolean":
            value = True if child.text.lower() == "true" else False
        elif type == "dateTime":
            value = iso8601.parse_date(child.text)
        elif type == "decimal":
            value = decimal.Decimal(child.text)
        elif type == "integer":
            value = int(child.text)
        else:
            value = child.text

        d[child.tag] = value
    return d


def _prepare_params(dirty_params, prefix=None):
    """Prepares parameters to be sent to challonge.com.

    The `prefix` can be used to convert parameters with keys that
    look like ("name", "url", "tournament_type") into something like
    ("tournament[name]", "tournament[url]", "tournament[tournament_type]"),
    which is how challonge.com expects parameters describing specific
    objects.

    """
    if prefix and prefix.endswith('[]'):
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
                    params.append(("%s[][%s]" % (prefix, k), val))
                    # params["%s[%s]" % (prefix, k)] = v
                else:
                    params.append((k+"[]", val))
                    # params[k] = v
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
