# Release History

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
