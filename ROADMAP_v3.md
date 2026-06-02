# pychallonge v3.0 Roadmap

## Current state (v2.1 branch)

- Sync-only, httpx `request()` (stateless)
- Returns plain `dict` / `list[dict]` — no typing
- API v1 (`api.challonge.com/v1`), HTTP Basic auth
- Global mutable state (`_credentials`, `tz`)

---

## Phase 1 — Async + Client Refactor

**Goal:** Replace global mutable state with a proper client class and add async support.

**Design:**

```python
# Sync
client = challonge.Client(user="x", api_key="y")
t = client.tournaments.show("my-tourney")

# Async
async with challonge.AsyncClient(user="x", api_key="y") as client:
    t = await client.tournaments.show("my-tourney")
```

**New module: `challonge/client.py`**

- `Client` — wraps `httpx.Client`, holds credentials and timezone
- `AsyncClient` — wraps `httpx.AsyncClient`, implements `__aenter__`/`__aexit__`
- `client.tournaments`, `client.participants`, `client.matches`, `client.attachments` are sub-clients bound to the parent
- `api.py` becomes internal helpers; module-level functions become thin wrappers around a default `Client` for backwards compatibility
- `async_fetch()` uses `await client.request(...)` — all domain coroutines just `await` it

**No new dependencies** — httpx already supports both sync and async natively.

---

## Phase 2 — DataClass Models

**Goal:** `fetch_and_parse()` returns typed objects instead of raw dicts.

**New module: `challonge/models.py`**

```python
@dataclass
class Tournament:
    id: int
    name: str
    url: str
    tournament_type: str
    state: str
    game_name: str | None = None
    private: bool = False
    starts_at: datetime | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

@dataclass
class Participant:
    id: int
    tournament_id: int
    name: str
    seed: int
    active: bool
    final_rank: int | None = None
    username: str | None = None
    group_id: int | None = None
    misc: str | None = None
    checked_in_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

@dataclass
class Match:
    id: int
    tournament_id: int
    state: str
    round: int
    identifier: str
    scores: str
    player1_id: int | None = None
    player2_id: int | None = None
    winner_id: int | None = None
    suggested_play_order: int | None = None
    score_in_sets: list | None = None
    tie: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

@dataclass
class MatchAttachment:
    id: int
    url: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

**Changes to `_parse()`:**

- Receives a `target_class: type[T]` argument
- After unwrapping the envelope and converting `_at` fields, constructs and returns `T(**d)`
- Uses `dataclasses.fields()` to filter only known keys — handles API adding new fields gracefully

**Breaking change:** dict → dataclass (attribute access is a superset for most use cases, but not drop-in). This is intentional and justifies the major version bump.

---

## Phase 3 — Challonge API v2.1

**Goal:** Target the new `api.challonge.com/v2.1` endpoint with full JSON:API support.

### Protocol changes

| Concern | v1 (current) | v2.1 (new) |
|---|---|---|
| Base URL | `api.challonge.com/v1` | `api.challonge.com/v2.1` |
| Auth | `httpx auth=(user, key)` Basic | Headers: `Authorization-Type: v1` + `Authorization: {key}` (or OAuth2 Bearer) |
| `Content-Type` | not required | `application/vnd.api+json` (mandatory) |
| `Accept` | not required | `application/json` (mandatory) |
| Request body | form-encoded bracket-notation | `{"data": {"type": "...", "attributes": {...}}}` |
| Response envelope | `{"tournament": {...}}` | `{"data": {"id": "...", "type": "...", "attributes": {...}}}` |
| List response | `[{"tournament": {...}}]` | `{"data": [...]}` with `page`/`per_page` pagination |
| DELETE return | body | 204 No Content |
| Errors | `{"errors": [...]}` | `{"errors": [{"status": 422, "detail": "...", "source": {"pointer": "..."}}]}` |

### `api.py` changes

- `_prepare_params()` eliminated — replaced by `_build_body(type, attributes)`
- `fetch()` auth switches from `httpx auth=` to explicit headers
- `_parse()` rewritten: unwraps `data.attributes`, flattens `timestamps` and `states` sub-objects, handles both single object and list shapes
- Note: match attachment timestamps use `createdAt`/`updatedAt` (camelCase) — API inconsistency, handle explicitly in `_parse()`

### Endpoint mapping

**Tournaments**
```
GET  /tournaments.json                              list (+ page, per_page, state, type, created_after/before)
POST /tournaments.json                              create
GET  /tournaments/{id}.json                         show
PUT  /tournaments/{id}.json                         update
DEL  /tournaments/{id}.json                         destroy
PUT  /tournaments/{id}/change_state.json            replaces: start, finalize, reset,
                                                              process_check_ins, abort_check_in,
                                                              open_for_predictions
     state values: start | finalize | reset | process_checkin | abort_checkin
                   | open_predictions | start_group_stage | finalize_group_stage | reset_group_stage
```

**Participants**
```
GET  /tournaments/{id}/participants.json            list (+ page, per_page)
POST /tournaments/{id}/participants.json            create
GET  /tournaments/{id}/participants/{id}.json       show
PUT  /tournaments/{id}/participants/{id}.json       update
DEL  /tournaments/{id}/participants/{id}.json       destroy
POST /tournaments/{id}/participants/bulk_add.json   bulk create (max 20, body: data.attributes.participants[])
DEL  /tournaments/{id}/participants/clear.json      clear all (new)
POST /tournaments/{id}/participants/randomize.json  randomize
POST /tournaments/{id}/participants/{id}/register   OAuth self-registration (new)
DEL  /tournaments/{id}/participants/{id}/register   OAuth self-unregistration (new)
```

**Matches**
```
GET  /tournaments/{id}/matches.json                 list (+ page, per_page, state, participant_id)
GET  /tournaments/{id}/matches/{id}.json            show
PUT  /tournaments/{id}/matches/{id}.json            update (body format changed — see below)
PUT  /tournaments/{id}/matches/{id}/change_state.json
     state values: reopen | mark_as_underway | unmark_as_underway
```

Match update request body (v2.1):
```json
{
  "data": {
    "type": "match",
    "attributes": {
      "match": [
        {"participant_id": "355", "score_set": "2-0", "rank": 1, "advancing": true}
      ],
      "tie": false,
      "location": "Table 1",
      "scheduled_time": "2024-01-01T10:00:00Z"
    }
  }
}
```

**Match Attachments**
```
GET  /tournaments/{id}/matches/{id}/attachments.json          list
POST /tournaments/{id}/matches/{id}/attachments.json          create
GET  /tournaments/{id}/matches/{id}/attachments/{id}.json     show
PUT  /tournaments/{id}/matches/{id}/attachments/{id}.json     update
DEL  /tournaments/{id}/matches/{id}/attachments/{id}.json     destroy
```

### Response field structure (v2.1)

**Participant** — `states` and `timestamps` are nested sub-objects in the API response, flattened by `_parse()`:
```json
{
  "id": "76", "type": "participant",
  "attributes": {
    "name": "Player 1", "seed": 1, "tournament_id": 21,
    "username": null, "final_rank": 1, "group_id": null,
    "states": {"active": true},
    "misc": "",
    "timestamps": {"created_at": "2023-04-21T14:29:06.374Z", "updated_at": null}
  }
}
```

**Match** — player references in `relationships`, also flattened by `_parse()`:
```json
{
  "id": "8008135", "type": "match",
  "attributes": {
    "state": "complete", "round": 1, "identifier": "A",
    "scores": "2 - 0", "winner_id": 355,
    "score_in_sets": [[3,1],[4,2]],
    "points_by_participant": [],
    "timestamps": {"created_at": "2023-04-21T14:29:06.374Z", "updated_at": null},
    "relationships": {
      "player1": {"data": {"id": "355", "type": "participant"}},
      "player2": {"data": {"id": "354", "type": "participant"}}
    }
  }
}
```

### v2.1 changelog highlights (from Challonge docs)

- Attribute naming is now consistently `snake_case` (v2.0 used inconsistent camelCase)
- Tournament IDs are integer IDs again (v2.0 used URL-based identifiers); URL is still supported
- Match winner field renamed `winners` → `winner_id`
- Group stage support: new attributes `group_stage_enabled`, `group_stage_options`
- Tie support for round robin and swiss via `tie: true` in match update
- `station_options` tournament attribute for station management

---

## Phase 4 — Stations & Station Queuers

**Goal:** Implement the two new v2.1-only resource types for managing physical play stations and their match queues.

**Concepts:**

- **Station** — a physical play area (PC, console, stream desk) scoped to a tournament. A station can have one active match assigned via `match_id`.
- **Station Queuer** — a match queued to play at a station, with an ordered `position`. The station's waitlist.
- Tournament opt-in via `station_options` in the tournament attributes (`auto_assign`, `only_start_matches_with_assigned_stations`).

**Depends on:** Phase 2 (dataclasses) and Phase 3 (v2.1). No v1 equivalents exist.

### New module: `challonge/stations.py`

```
GET  /tournaments/{id}/stations.json                list (+ page, per_page, community_id)
POST /tournaments/{id}/stations.json                create
GET  /tournaments/{id}/stations/{station_id}.json   show
PUT  /tournaments/{id}/stations/{station_id}.json   update
DEL  /tournaments/{id}/stations/{station_id}.json   destroy (returns 200 + body, not 204)
```

**Station dataclass:**
```python
@dataclass
class Station:
    id: int
    name: str                    # required on create/update
    stream_url: str | None = None
    details: str | None = None   # private, visible only to assigned players
    match_id: int | None = None  # currently assigned match
```

**Functions:**
```python
def index(tournament) -> list[Station]
def create(tournament, name, *, stream_url=None, details=None) -> Station
def show(tournament, station_id) -> Station
def update(tournament, station_id, **params) -> Station
def destroy(tournament, station_id) -> Station    # returns the deleted station
```

> **Note:** The raw API doc lists `type: "participant"` in the update request body — this is a doc typo. We send `type: "station"` and verify against the live API.

### New module: `challonge/station_queuers.py`

```
GET  /tournaments/{id}/stations/{sid}/station_queuers.json              list (+ page, per_page)
POST /tournaments/{id}/stations/{sid}/station_queuers.json              create
GET  /tournaments/{id}/stations/{sid}/station_queuers/{qid}.json        show
PUT  /tournaments/{id}/stations/{sid}/station_queuers/{qid}.json        update
DEL  /tournaments/{id}/stations/{sid}/station_queuers/{qid}.json        destroy
```

**StationQueuer dataclass:**
```python
@dataclass
class StationQueuer:
    id: int
    match_id: int                # required — the match to queue
    position: int | None = None  # insertion position in the queue
```

**Functions:**
```python
def index(tournament, station_id) -> list[StationQueuer]
def create(tournament, station_id, match_id, *, position=None) -> StationQueuer
def show(tournament, station_id, queuer_id) -> StationQueuer
def update(tournament, station_id, queuer_id, match_id, *, position=None) -> StationQueuer
def destroy(tournament, station_id, queuer_id) -> None
```

---

## Summary

| Phase | What | Key deliverables | Effort | Release |
|-------|------|-----------------|--------|---------|
| **1** | Async + Client refactor | `client.py` with `Client` / `AsyncClient`, kill global state | Medium | v3.0 ✅ |
| **2** | DataClass models | `models.py` with `Tournament`, `Participant`, `Match`, `MatchAttachment` | Medium | v3.0 ✅ |
| **3** | Challonge API v2.1 | New auth headers, JSON:API body/parse, `change_state` endpoints, pagination | High | v4.0 |
| **4** | Stations & Station Queuers | `stations.py`, `station_queuers.py`, `Station` + `StationQueuer` dataclasses | Low | v4.0 |

Phases 1 and 2 shipped as v3.0. Phases 3 and 4 continue in v4.0.
