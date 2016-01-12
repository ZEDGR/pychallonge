from challonge import api


def index(**params):
    """Retrieve a set of tournaments created with your account."""
    return api.fetch_and_parse("GET", "tournaments", **params)


def create(name, url, tournament_type="single elimination", **params):
    """Create a new tournament."""
    params.update({
        "name": name,
        "url": url,
        "tournament_type": tournament_type,
    })

    return api.fetch_and_parse("POST", "tournaments", "tournament", **params)


def show(tournament):
    """Retrieve a single tournament record created with your account."""
    return api.fetch_and_parse("GET", "tournaments/%s" % tournament)


def update(tournament, **params):
    """Update a tournament's attributes."""
    api.fetch("PUT", "tournaments/%s" % tournament, "tournament", **params)


def destroy(tournament):
    """Deletes a tournament along with all its associated records.

    There is no undo, so use with care!

    """
    api.fetch("DELETE", "tournaments/%s" % tournament)


def process_check_ins(tournament):
    """This should be invoked after a tournament's
    check-in window closes before the tournament is started.

    1) Marks participants who have not checked in as inactive.
    2) Moves inactive participants to bottom seeds (ordered by original seed).
    3) Transitions the tournament state from 'checking_in' to 'checked_in'

    """
    api.fetch("POST", "tournaments/%s/process_check_ins")


def abort_check_in(tournament):
    """When your tournament is in a 'checking_in' or 'checked_in' state,
    there's no way to edit the tournament's start time (start_at)
    or check-in duration (check_in_duration).
    You must first abort check-in, then you may edit those attributes.

    1) Makes all participants active and clears their checked_in_at times.
    2) Transitions the tournament state from 'checking_in' or 'checked_in' to 'pending'

    """
    api.fetch("POST", "tournaments/%s/abort_check_in")


def start(tournament):
    """Start a tournament, opening up matches for score reporting.

    The tournament must have at least 2 participants.

    """
    api.fetch("POST", "tournaments/%s/start" % tournament)


def finalize(tournament):
    """Finalize a tournament that has had all match scores submitted,
    rendering its results permanent.

    """
    api.fetch("POST", "tournaments/%s/finalize" % tournament)


def reset(tournament):
    """Reset a tournament, clearing all of its scores and attachments.

    You can then add/remove/edit participants before starting the
    tournament again.

    """
    api.fetch("POST", "tournaments/%s/reset" % tournament)
