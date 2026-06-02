from challonge.models import MatchAttachment


class AttachmentsClient:
    def __init__(self, client):
        self._c = client

    def index(self, tournament, match_id):
        return self._c._fetch_and_parse(
            "GET",
            f"tournaments/{tournament}/matches/{match_id}/attachments",
            target_class=MatchAttachment,
        )

    def create(self, tournament, match_id, **params):
        return self._c._fetch_and_parse(
            "POST",
            f"tournaments/{tournament}/matches/{match_id}/attachments",
            "match_attachment",
            target_class=MatchAttachment,
            **params,
        )

    def show(self, tournament, match_id, attachment_id):
        return self._c._fetch_and_parse(
            "GET",
            f"tournaments/{tournament}/matches/{match_id}/attachments/{attachment_id}",
            target_class=MatchAttachment,
        )

    def update(self, tournament, match_id, attachment_id, **params):
        return self._c._fetch_and_parse(
            "PUT",
            f"tournaments/{tournament}/matches/{match_id}/attachments/{attachment_id}",
            "match_attachment",
            target_class=MatchAttachment,
            **params,
        )

    def destroy(self, tournament, match_id, attachment_id):
        return self._c._fetch(
            "DELETE",
            f"tournaments/{tournament}/matches/{match_id}/attachments/{attachment_id}",
        )
