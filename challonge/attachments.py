from challonge import api


def index(tournament, match):
    """Retrieve a set of attachments created for a specific match."""
    return api.fetch_and_parse("GET", "tournaments/%s/matches/%s/attachments" % (tournament, match))


def create(tournament, match, **params):
    """Create a new attachment for the specific match."""
    return api.fetch_and_parse(
        "POST",
        "tournaments/%s/matches/%s/attachments" % (tournament, match),
        "match_attachment",
        **params
    )


def show(tournament, match, attachment):
    """Retrieve a single match attachment record."""
    return api.fetch_and_parse(
        "GET", "tournaments/%s/matches/%s/attachments/%s" % (tournament, match, attachment)
    )


def update(tournament, match, attachment, **params):
    """Update the attributes of a match attachment."""
    api.fetch(
        "PUT",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match, attachment),
        "match_attachment",
        **params
    )


def destroy(tournament, match, attachment):
    """Delete a match attachment."""
    api.fetch(
        "DELETE", "tournaments/%s/matches/%s/attachments/%s" % (tournament, match, attachment)
    )
