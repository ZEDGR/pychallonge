from challonge import api


def index(tournament, **params):
    """Retrieve a tournament's match list."""
    return api.fetch_and_parse("GET", "tournaments/%s/matches" % tournament, **params)


def show(tournament, match_id, **params):
    """Retrieve a single match record for a tournament."""
    return api.fetch_and_parse(
        "GET", "tournaments/%s/matches/%s" % (tournament, match_id), **params
    )


def update(tournament, match_id, **params):
    """Update/submit the score(s) for a match."""
    api.fetch("PUT", "tournaments/%s/matches/%s" % (tournament, match_id), "match", **params)


def reopen(tournament, match_id):
    """Reopens a match that was marked completed, automatically resetting matches that follow it."""
    api.fetch("POST", "tournaments/%s/matches/%s/reopen" % (tournament, match_id))


def mark_as_underway(tournament, match_id):
    """Sets "underway_at" to the current time and highlights the match in the bracket"""
    api.fetch("POST", "tournaments/%s/matches/%s/mark_as_underway" % (tournament, match_id))


def unmark_as_underway(tournament, match_id):
    """Clears "underway_at" and unhighlights the match in the bracket"""
    api.fetch("POST", "tournaments/%s/matches/%s/unmark_as_underway" % (tournament, match_id))
