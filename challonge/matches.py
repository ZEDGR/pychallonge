from challonge.models import Match


class MatchesClient:
    def __init__(self, client):
        self._c = client

    def index(self, tournament, **params):
        return self._c._fetch_and_parse("GET", f"tournaments/{tournament}/matches", target_class=Match, **params)

    def show(self, tournament, match_id, **params):
        return self._c._fetch_and_parse("GET", f"tournaments/{tournament}/matches/{match_id}", target_class=Match, **params)

    def update(self, tournament, match_id, **params):
        return self._c._fetch_and_parse("PUT", f"tournaments/{tournament}/matches/{match_id}", "match", target_class=Match, **params)

    def reopen(self, tournament, match_id):
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/matches/{match_id}/reopen", target_class=Match)

    def mark_as_underway(self, tournament, match_id):
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/matches/{match_id}/mark_as_underway", target_class=Match)

    def unmark_as_underway(self, tournament, match_id):
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/matches/{match_id}/unmark_as_underway", target_class=Match)
