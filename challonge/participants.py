from challonge import api


def index(tournament):
    """Retrieve a tournament's participant list.

    Args:
        tournament (int or str): The tournament's id or name

    Returns:
        A list with the tournament's participants
    """
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/participants" % tournament)


def create(tournament, name, **params):
    """Add a participant to a tournament.

    Args:
        tournament (int or str): The tournament's id or name
        name (str): The participant's name
        **params (optional): extra keyword arguments used for the setup of the participant

    Returns:
        A dict representing the created participant
    """
    params.update({"name": name})

    return api.fetch_and_parse(
        "POST",
        "tournaments/%s/participants" % tournament,
        "participant",
        **params)


def bulk_add(tournament, names, **params):
    """Bulk add participants to a tournament (up until it is started).

    Args:
        tournament (int or str): The tournament's id or name
        names (list): A list of participants names (str)
        **params (optional): extra keyword arguments used for the setup of the participants

    Returns:
        A list representing the created participants
    """
    params.update({"name": names})

    return api.fetch_and_parse(
        "POST",
        "tournaments/%s/participants/bulk_add" % tournament,
        "participants[]",
        **params)


def show(tournament, participant_id, **params):
    """Retrieve a single participant record for a tournament.

    Args:
        tournament (int or str): The tournament's id or name
        participant_id (int): The participant's id for the specific tournament
        **params (optional): The keywords arguments to include matches.

    Returns:
        A dict with the match details
    """
    return api.fetch_and_parse(
        "GET",
        "tournaments/%s/participants/%s" % (tournament, participant_id),
        **params)


def update(tournament, participant_id, **params):
    """Update the attributes of a tournament participant.

    Args:
        tournament (int or str): The tournament's id or name
        participant_id (int): The participant's id for the specific tournament
        **params (optional): The keywords arguments used to update the participant.

    Returns:
        None
    """
    api.fetch(
        "PUT",
        "tournaments/%s/participants/%s" % (tournament, participant_id),
        "participant",
        **params)


def check_in(tournament, participant_id):
    """Checks a participant in.

    Args:
        tournament (int or str): The tournament's id or name
        participant_id (int): The participant's id for the specific tournament

    Returns:
        None
    """
    api.fetch(
        "POST",
        "tournaments/%s/participants/%s/check_in" % (tournament, participant_id))


def undo_check_in(tournament, participant_id):
    """Marks a participant as having not checked in.

    Args:
        tournament (int or str): The tournament's id or name
        participant_id (int): The participant's id for the specific tournament

    Returns:
        None
    """
    api.fetch(
        "POST",
        "tournaments/%s/participants/%s/undo_check_in" % (tournament, participant_id))


def destroy(tournament, participant_id):
    """Destroys or deactivates a participant.

    If tournament has not started, delete a participant, automatically
    filling in the abandoned seed number.

    If tournament is underway, mark a participant inactive, automatically
    forfeiting his/her remaining matches.

    Args:
        tournament (int or str): The tournament's id or name
        participant_id (int): The participant's id for the specific tournament

    Returns:
        None
    """
    api.fetch(
        "DELETE",
        "tournaments/%s/participants/%s" % (tournament, participant_id))


def randomize(tournament):
    """Randomize seeds among participants.

    Only applicable before a tournament has started.

    Args:
        tournament (int or str): The tournament's id or name
        participant_id (int): The participant's id for the specific tournament

    Returns:
        None
    """
    api.fetch("POST", "tournaments/%s/participants/randomize" % tournament)
