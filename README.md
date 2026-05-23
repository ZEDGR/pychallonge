# pychallonge

Lightweight Python wrapper for the [Challonge API](http://api.challonge.com/v1).
The pychallonge module was created by [Russ Amos](https://github.com/russ-)

# Python version support

- `3.10+`

# Installation

For the stable version

    pip install pychallonge

For latest development

    pip install -e git+https://github.com/ZEDGR/pychallonge#egg=pychallonge

# Usage

```python
import challonge

# Tell pychallonge about your [Challonge API credentials](http://api.challonge.com/v1).
challonge.set_credentials("your_challonge_username", "your_api_key")

# Retrieve a tournament by its id (or its url).
tournament = challonge.tournaments.show(3272)

# Tournaments, matches, and participants are all represented as normal Python dicts.
print(tournament["id"]) # 3272
print(tournament["name"]) # My Awesome Tournament
print(tournament["started_at"]) # None

# Retrieve the participants for a given tournament.
participants = challonge.participants.index(tournament["id"])
print(len(participants)) # 13

# Mutations (POST/PUT) return the updated resource directly.
tournament = challonge.tournaments.start(tournament["id"])
print(tournament["started_at"]) # 2011-07-31 16:16:02-04:00
```

See [challonge.com](http://api.challonge.com/v1) for full API documentation.

# API Issues

The Challonge API has some issues with the attachments endpoints. When uploading
an attachment with a file (asset), the API returns a 500 internal server error.
This issue has been reported to Challonge.

The check-in undo endpoint has unexpected behaviour: the `checked_in` field in
the API response remains `True` even after a successful undo. The participant is
correctly marked as not checked in on the website.

Datetime fields from the API carry inconsistent timezone offsets. Pychallonge
normalises these to your machine's local timezone. You can also set a specific
timezone with the `set_timezone` function.

# Running the tests

Tests make real API calls and require a Challonge account. Set `CHALLONGE_USER`
and `CHALLONGE_KEY` in your environment before running.

    $ git clone https://github.com/ZEDGR/pychallonge
    $ cd pychallonge
    $ CHALLONGE_USER=my_user CHALLONGE_KEY=my_api_key uv run python -m unittest tests.py

Note that several tournaments are created and destroyed over the course of the
tests. If any test fails mid-run, orphaned tournaments can be cleaned up as follows:

```python
import challonge
challonge.set_credentials("my_user", "my_api_key")
for t in challonge.tournaments.index():
    if t["name"].startswith("pychal"):
        challonge.tournaments.destroy(t["id"])
```
