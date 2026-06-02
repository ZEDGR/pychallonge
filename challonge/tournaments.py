from challonge.models import Tournament


class TournamentsClient:
    def __init__(self, client):
        self._c = client

    def index(self, **params):
        return self._c._fetch_and_parse(
            "GET", "tournaments", target_class=Tournament, **params
        )

    def create(self, name, url, tournament_type="single elimination", **params):
        params.update({"name": name, "url": url, "tournament_type": tournament_type})
        return self._c._fetch_and_parse(
            "POST", "tournaments", "tournament", target_class=Tournament, **params
        )

    def show(self, tournament, **params):
        return self._c._fetch_and_parse(
            "GET", f"tournaments/{tournament}", target_class=Tournament, **params
        )

    def update(self, tournament, **params):
        return self._c._fetch_and_parse(
            "PUT",
            f"tournaments/{tournament}",
            "tournament",
            target_class=Tournament,
            **params,
        )

    def destroy(self, tournament):
        return self._c._fetch("DELETE", f"tournaments/{tournament}")

    def process_check_ins(self, tournament, **params):
        return self._c._fetch_and_parse(
            "POST",
            f"tournaments/{tournament}/process_check_ins",
            target_class=Tournament,
            **params,
        )

    def abort_check_in(self, tournament, **params):
        return self._c._fetch_and_parse(
            "POST",
            f"tournaments/{tournament}/abort_check_in",
            target_class=Tournament,
            **params,
        )

    def open_for_predictions(self, tournament, **params):
        return self._c._fetch_and_parse(
            "POST",
            f"tournaments/{tournament}/open_for_predictions",
            target_class=Tournament,
            **params,
        )

    def start(self, tournament, **params):
        return self._c._fetch_and_parse(
            "POST", f"tournaments/{tournament}/start", target_class=Tournament, **params
        )

    def finalize(self, tournament, **params):
        return self._c._fetch_and_parse(
            "POST",
            f"tournaments/{tournament}/finalize",
            target_class=Tournament,
            **params,
        )

    def reset(self, tournament, **params):
        return self._c._fetch_and_parse(
            "POST", f"tournaments/{tournament}/reset", target_class=Tournament, **params
        )
