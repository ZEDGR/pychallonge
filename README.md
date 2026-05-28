# pychallonge

Lightweight Python wrapper for the [Challonge API](http://api.challonge.com/v1).
The pychallonge module was created by [Russ Amos](https://github.com/russ-)

## Python version support

- 3.10 or later

## Installation

The `pychallonge` package is available on PyPI and you can install it through your favorite package manager:

    pip install pychallonge

## Usage

```python
from challonge import Client

# Create a client with your Challonge API credentials.
client = Client(user="your_challonge_username", api_key="your_api_key")

# Retrieve a tournament by its id (or its url).
tournament = client.tournaments.show(3272)

# Tournaments, matches, and participants are returned as typed dataclasses.
print(tournament.id)          # 3272
print(tournament.name)        # My Awesome Tournament
print(tournament.started_at)  # None

# Retrieve the participants for a given tournament.
participants = client.participants.index(tournament.id)
print(len(participants))  # 13

# Mutations (POST/PUT) return the updated resource directly.
tournament = client.tournaments.start(tournament.id)
print(tournament.started_at)  # 2011-07-31 16:16:02-04:00

# Close the client when done, or use it as a context manager.
client.close()
```

### Context manager

```python
with Client(user="your_challonge_username", api_key="your_api_key") as client:
    tournament = client.tournaments.show(3272)
```

### Async

```python
from challonge import AsyncClient

async with AsyncClient(user="your_challonge_username", api_key="your_api_key") as client:
    tournament = await client.tournaments.show(3272)
    participants = await client.participants.index(tournament.id)
```

### Timezone

By default datetime fields are normalised to your machine's local timezone. Pass a timezone string to override:

```python
client = Client(user="your_challonge_username", api_key="your_api_key", timezone="UTC")
```

See [challonge.com](http://api.challonge.com/v1) for full API documentation.

## API Issues

The Challonge API has some issues with the attachments endpoints. When uploading
an attachment with a file (asset), the API returns a 500 internal server error.
This issue has been reported to Challonge.

The check-in undo endpoint has unexpected behaviour: the `checked_in` field in
the API response remains `True` even after a successful undo. The participant is
correctly marked as not checked in on the website.

## Running the tests

Tests make real API calls and require a Challonge account. Set `CHALLONGE_USER`
and `CHALLONGE_KEY` in your environment before running.

    $ git clone https://github.com/ZEDGR/pychallonge
    $ cd pychallonge
    $ CHALLONGE_USER=my_user CHALLONGE_KEY=my_api_key uv run pytest tests.py -v

Note that several tournaments are created and destroyed over the course of the
tests. If any test fails mid-run, orphaned tournaments can be cleaned up as follows:

```python
from challonge import Client

with Client(user="my_user", api_key="my_api_key") as client:
    for t in client.tournaments.index():
        if t.name.startswith("pychal"):
            client.tournaments.destroy(t.id)
```
