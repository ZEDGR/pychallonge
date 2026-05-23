from challonge import api


def index(tournament, **params):
    """Retrieve a tournament's match list.

    Args:
        tournament (int or str): The tournament's id or name
        **params (optional): the keyword arguments used to filter the results with state and/or participant_id

    Returns:
        A list with the tournament's matches
    """
    return api.fetch_and_parse("GET", f"tournaments/{tournament}/matches", **params)


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
        "GET", f"tournaments/{tournament}/matches/{match_id}", **params
    )


def update(tournament, match_id, **params):
    """Update/submit the score(s) for a match.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        **params (optional): the keyword arguments used to update of the match

    Returns:
        A dict representing the updated match
    """
    return api.fetch_and_parse(
        "PUT", f"tournaments/{tournament}/matches/{match_id}", "match", **params
    )


def reopen(tournament, match_id):
    """Reopens a match that was marked completed, automatically resetting matches that follow it.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        A dict representing the reopened match
    """
    return api.fetch_and_parse(
        "POST", f"tournaments/{tournament}/matches/{match_id}/reopen"
    )


def mark_as_underway(tournament, match_id):
    """Sets "underway_at" to the current time and highlights the match in the bracket.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        A dict representing the match with underway_at set
    """
    return api.fetch_and_parse(
        "POST", f"tournaments/{tournament}/matches/{match_id}/mark_as_underway"
    )


def unmark_as_underway(tournament, match_id):
    """Clears "underway_at" and unhighlights the match in the bracket.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        A dict representing the match with underway_at cleared
    """
    return api.fetch_and_parse(
        "POST", f"tournaments/{tournament}/matches/{match_id}/unmark_as_underway"
    )
