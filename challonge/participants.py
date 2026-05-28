from challonge.models import Participant


class ParticipantsClient:
    def __init__(self, client):
        self._c = client

    def index(self, tournament):
        return self._c._fetch_and_parse("GET", f"tournaments/{tournament}/participants", target_class=Participant)

    def create(self, tournament, name, **params):
        params.update({"name": name})
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/participants", "participant", target_class=Participant, **params)

    def bulk_add(self, tournament, names, **params):
        params.update({"name": names})
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/participants/bulk_add", "participants[]", target_class=Participant, **params)

    def show(self, tournament, participant_id, **params):
        return self._c._fetch_and_parse("GET", f"tournaments/{tournament}/participants/{participant_id}", target_class=Participant, **params)

    def update(self, tournament, participant_id, **params):
        return self._c._fetch_and_parse("PUT", f"tournaments/{tournament}/participants/{participant_id}", "participant", target_class=Participant, **params)

    def check_in(self, tournament, participant_id):
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/participants/{participant_id}/check_in", target_class=Participant)

    def undo_check_in(self, tournament, participant_id):
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/participants/{participant_id}/undo_check_in", target_class=Participant)

    def destroy(self, tournament, participant_id):
        return self._c._fetch("DELETE", f"tournaments/{tournament}/participants/{participant_id}")

    def randomize(self, tournament):
        return self._c._fetch_and_parse("POST", f"tournaments/{tournament}/participants/randomize", target_class=Participant)
