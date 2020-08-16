from challonge import api


def index(tournament, match_id):
    """Retrieve a set of attachments created for a specific match."""
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/matches/%s/attachments" % (tournament, match_id))


def create(tournament, match_id, **params):
    """Create a new attachment for the specific match."""
    return api.fetch_and_parse(
        "POST",
        "tournaments/%s/matches/%s/attachments" % (tournament, match_id),
        "match_attachment",
        **params)


def show(tournament, match_id, attachment_id):
    """Retrieve a single match attachment record."""
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match_id, attachment_id))


def update(tournament, match_id, attachment_id, **params):
    """Update the attributes of a match attachment."""
    api.fetch(
        "PUT",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match_id, attachment_id),
        "match_attachment",
        **params)


def destroy(tournament, match_id, attachment_id):
    """Delete a match attachment."""
    api.fetch(
        "DELETE",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match_id, attachment_id))
