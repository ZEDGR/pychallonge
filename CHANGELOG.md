# Release History

## 3.0.0 (2026-06-02)

**Breaking Changes**

- Replace module-level functions with a `Client` / `AsyncClient` class — all calls now go through an instance (`client.tournaments.show(...)` instead of `challonge.tournaments.show(...)`)
- API responses are now typed dataclasses (`Tournament`, `Participant`, `Match`, `MatchAttachment`) instead of plain dicts — use attribute access (`t.name`) instead of key access (`t["name"]`)
- `set_credentials()`, `set_timezone()`, and other module-level state helpers removed — pass `user`, `api_key`, and `timezone` to the `Client` constructor instead
- `fetch()` / `fetch_and_parse()` are no longer public

**New Features**

- `AsyncClient` with full async/await support via `httpx.AsyncClient` — all domain methods are awaitable
- Context manager support: `with Client(...) as client` and `async with AsyncClient(...) as client`
- `timezone` parameter on `Client` / `AsyncClient` accepts IANA timezone strings (e.g. `"Asia/Seoul"`)
- New `models.py` module with `Tournament`, `Participant`, `Match`, and `MatchAttachment` dataclasses

**Improvements**

- Switch from unittest to pytest
- Add async smoke tests covering all four resource domains

## 2.0.0 (2026-05-24)

**Breaking Changes**

- Require Python 3.10+
- Drop Python 2 support
- Replace `requests` with `httpx` for HTTP requests
- Remove `pytz` dependency in favour of stdlib `zoneinfo`

**Improvements**

- All PUT and POST endpoints now return the updated resource directly,
  eliminating the need for a follow-up API call to retrieve the result.
  Affected functions: `tournaments.update`, `participants.update`,
  `participants.check_in`, `participants.undo_check_in`,
  `participants.randomize`, `matches.update`, `matches.reopen`,
  `matches.mark_as_underway`, `matches.unmark_as_underway`,
  `attachments.update`
- Add `timeout` parameter to `fetch` and `fetch_and_parse`
- Add docstrings to all modules
- Migrate from Poetry to uv for package management
- Replace `setup.py` with `pyproject.toml` using hatchling as build backend
- Replace Travis CI/CD with GitHub Actions
- Add GitHub Actions workflow for publishing to PyPI

**Bugfixes**

- Fix user-agent not being sent correctly in HTTP requests
- Fix `_prepare_params` not being called in `fetch()`
- Fix `undo_check_in` test incorrectly calling the same participant twice

## 1.11.2 (2021-03-28)

**Improvements**

- Convert CHANGELOG to markdown format
- Convert README to markdown format
- Add extra information about the handover of this module from Russ Amos

## 1.11.1 (2021-03-27)

**Bugfixes**

- Fix issue with packaging

## 1.11.0 (2021-03-27)

**Bugfixes**

- Fix issue with user-agent on HTTP requests. The Challonge API does
  not respond with the requests module default user-agent

## 1.10.0 (2020-08-10)

**Improvements**

- Add support for tournaments.open_for_predictions endpoint

## 1.9.0 (2020-03-16)

**Improvements**

- Add support for the new endpoints mark and umark as underway for
  matches
- Pin versions for dependencies

## 1.8.1 (2017-11-12)

**Bugfixes**

- Fix parsing issues with fields: name, display_name,
  display_name_with_invitation_email_address, username,
  challonge_username

## 1.8.0 (2017-04-22)

**Improvements**

- Add support for the new match reopen endpoint.
- Add functions get_timezone(), set_timezone().

**Bugfixes**

- Fix random timezone offset returned by the API in all date/time
  fields. Instead your machine's local timezone will be returned.

## 1.7.0 (2016-12-26)

**Improvements**

- Drop XML endpoints support. Welcome JSON endpoints support.
  (slightly better performance for the whole module)
- Partial support for attachments(why partial? see README in API
  Issues section)

**Bugfixes**

- Build the correct request for POST and PUT methods. That was not a
  bug actually but I wanted to be right.
- Add missing argument "params" for: matches-\>show,
  participants-\>show, tournaments-\>show,
  tournaments-\>process_check_ins, tournaments-\>abort_check_in,
  tournaments-\>start, tournaments-\>finalize, tournaments-\>reset.
- These tournament functions now returns the tournament:
  process_check_ins, abort_check_in, start, finalize

## 1.6.7 (2016-08-27)

**Improvements**

- Drop Python2.6 compatibility support
- Add support for Python3.4+
- Replace python-dateutil with iso8601 package(much lighter)
- Add new dependency: requests
- Remove publish function because publish end-point is deprecated
  since 2012-12-07 according to API changelog
- Add support for participants API end-points: bulk_add, check_in,
  undo_check_in
- Add support for tournaments API end-points: abort_check_in,
  process_check_ins, finalize

**Bugfixes**

- Fix non-breaking spaces bug for XML Parser(this only happens on
  Python2).
