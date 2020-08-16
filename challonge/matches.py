from challonge import api


def index(tournament, **params):
    """Retrieve a tournament's match list.

    Args:
        tournament (int or str): The tournament's id or name
        **params (optional): the keyword arguments used to filter the results with state and/or participant_id

    Returns:
        A list with the tournament's matches
    """
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/matches" % tournament,
        **params)


def show(tournament, match_id, **params):
    """Retrieve a single match record for a tournament.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        **params (optional): The keywords arguments to include attachments.

    Returns:
        A dict with the match details
    """
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/matches/%s" % (tournament, match_id),
        **params)


def update(tournament, match_id, **params):
    """Update/submit the score(s) for a match.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        **params (optional): the keyword arguments used to filter the results with state and/or participant_id

    Returns:
        None
    """
    api.fetch(
        "PUT",
        "tournaments/%s/matches/%s" % (tournament, match_id),
        "match",
        **params)


def reopen(tournament, match_id):
    """Reopens a match that was marked completed, automatically resetting matches that follow it.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        None
    """
    api.fetch(
        "POST",
        "tournaments/%s/matches/%s/reopen" % (tournament, match_id))


def mark_as_underway(tournament, match_id):
    """Sets "underway_at" to the current time and highlights the match in the bracket.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        None
    """
    api.fetch(
        "POST",
        "tournaments/%s/matches/%s/mark_as_underway" % (tournament, match_id))


def unmark_as_underway(tournament, match_id):
    """Clears "underway_at" and unhighlights the match in the bracket.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        None
    """
    api.fetch(
        "POST",
        "tournaments/%s/matches/%s/unmark_as_underway" % (tournament, match_id))
