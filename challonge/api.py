import decimal
import urllib
import urllib2
import dateutil.parser
import itertools
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
    params = urllib.urlencode(_prepare_params(params, params_prefix))

    # build the HTTP request
    url = "https://%s/%s.xml" % (CHALLONGE_API_URL, uri)
    if method == "GET":
        req = urllib2.Request("%s?%s" % (url, params))
    else:
        req = urllib2.Request(url)
        req.add_data(params)
    req.get_method = lambda: method

    # use basic authentication
    user, api_key = get_credentials()
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm="Application",
        uri=req.get_full_url(),
        user=user,
        passwd=api_key
    )
    opener = urllib2.build_opener(auth_handler)

    try:
        response = opener.open(req)
    except urllib2.HTTPError, e:
        if e.code != 422:
            raise
        # wrap up application-level errors
        doc = ElementTree.parse(e).getroot()
        if doc.tag != "errors":
            raise
        errors = [e.text for e in doc]
        raise ChallongeException(*errors)

    return response


def fetch_and_parse(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return the root Element of the response."""
    doc = ElementTree.parse(fetch(method, uri, params_prefix, **params))
    return _parse(doc.getroot())


def _parse(root):
    """Recursively convert an Element into python data types"""
    if root.tag == "nil-classes":
        return []
    elif root.get("type") == "array":
        return [_parse(child) for child in root]
    elif len(root):
        return {child.tag: _parse(child) for child in root}

    type = root.get("type") or "string"

    if root.get("nil"):
        value = None
    elif type == "boolean":
        value = True if root.text.lower() == "true" else False
    elif type == "dateTime":
        value = dateutil.parser.parse(root.text)
    elif type == "decimal":
        value = decimal.Decimal(root.text)
    elif type == "integer":
        value = int(root.text)
    else:
        value = root.text

    return value


def _prepare_params(dirty_params, prefix=None):
    """Prepares parameters to be sent to challonge.com.

    The `prefix` can be used to convert parameters with keys that
    look like ("name", "url", "tournament_type") into something like
    ("tournament[name]", "tournament[url]", "tournament[tournament_type]"),
    which is how challonge.com expects parameters describing specific
    objects.

    """
    if prefix and prefix.endswith('[]'):
        arraykeys = []
        arrayvals = []
        for k,v in dirty_params.items():
            if isinstance(v,(list,tuple)):
                arraykeys.append(k)
                arrayvals.append(v)
        arrayiter = ((k,v) for vals in zip(*arrayvals) for k,v in zip(arraykeys,vals))
        restiter = ((k,v) for k,v in dirty_params.items() if k not in arraykeys)
        dpiter = itertools.chain(arrayiter,restiter)
    else:
        dpiter = dirty_params.items()

    params = []
    for k, v in dpiter:
        if isinstance(v,(list,tuple)):
            for w in v:
                w = _prepare_value(w)
                if prefix:
                    params.append(("%s[%s][]" % (prefix, k),w))
                else:
                    params.append((k+"[]",w))
        else:
            v = _prepare_value(v)
            if prefix:
                params.append(("%s[%s]" % (prefix, k),v))
            else:
                params.append((k,v))

    return params


def _prepare_value(val):
    if hasattr(val, "isoformat"):
        return val.isoformat()
    elif isinstance(val, bool):
        # challonge.com only accepts lowercase true/false
        return str(val).lower()
    else:
        return val
    
