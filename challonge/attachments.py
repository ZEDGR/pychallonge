from challonge import api


def index(tournament, match_id):
    """Retrieve a set of attachments created for a specific match.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament

    Returns:
        A list with the tournament's attachments
    """
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/matches/%s/attachments" % (tournament, match_id))


def create(tournament, match_id, **params):
    """Create a new attachment for the specific match.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        **params (optional): extra keyword arguments used for the setup of the attachment (asset, url, description)

    Returns:
        A dict representing the created attachment
    """
    return api.fetch_and_parse(
        "POST",
        "tournaments/%s/matches/%s/attachments" % (tournament, match_id),
        "match_attachment",
        **params)


def show(tournament, match_id, attachment_id):
    """Retrieve a single match attachment record.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        attachment_id (int): The attachment's id for the specific match

    Returns:
        A dict representing the attachment
    """
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match_id, attachment_id))


def update(tournament, match_id, attachment_id, **params):
    """Update the attributes of a match attachment.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        attachment_id (int): The attachment's id for the specific match
        **params (optional): extra keyword arguments used for the update of the attachment (asset, url, description)


    Returns:
        None
    """
    api.fetch(
        "PUT",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match_id, attachment_id),
        "match_attachment",
        **params)


def destroy(tournament, match_id, attachment_id):
    """Delete a match attachment.

    Args:
        tournament (int or str): The tournament's id or name
        match_id (int): The match's id for the specific tournament
        attachment_id (int): The attachment's id for the specific match

    Returns:
        None
    """
    api.fetch(
        "DELETE",
        "tournaments/%s/matches/%s/attachments/%s" % (tournament, match_id, attachment_id))
