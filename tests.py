import datetime
import os
import random
import string

import httpx
import pytest
import tzlocal

import challonge

username = os.environ.get("CHALLONGE_USER")
api_key = os.environ.get("CHALLONGE_KEY")


def _get_random_name():
    return "pychal_" + "".join(
        random.choice(string.ascii_lowercase) for _ in range(0, 15)
    )


class TestAPI:
    def test_set_credentials(self):
        challonge.set_credentials(username, api_key)
        assert challonge.api._credentials["user"] == username
        assert challonge.api._credentials["api_key"] == api_key

    def test_get_credentials(self):
        challonge.api._credentials["user"] = username
        challonge.api._credentials["api_key"] = api_key
        assert challonge.get_credentials() == (username, api_key)

    def test_get_local_timezone(self):
        assert challonge.get_timezone() == tzlocal.get_localzone()

    def test_set_get_timezone(self):
        challonge.set_timezone("Asia/Seoul")
        assert str(challonge.get_timezone()) == "Asia/Seoul"

    def test_call(self):
        challonge.set_credentials(username, api_key)
        assert challonge.fetch("GET", "tournaments") != ""


class TestTournaments:
    @pytest.fixture(autouse=True)
    def setup(self):
        challonge.set_credentials(username, api_key)
        self.random_name = _get_random_name()
        self.t = challonge.tournaments.create(self.random_name, self.random_name)
        yield
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ts = list(
            filter(lambda x: x["id"] == self.t["id"], challonge.tournaments.index())
        )
        assert len(ts) == 1
        assert self.t == ts[0]

    def test_index_filter_by_state(self):
        ts = list(
            filter(
                lambda x: x["id"] == self.t["id"],
                challonge.tournaments.index(state="pending"),
            )
        )
        assert len(ts) == 1
        assert self.t == ts[0]

        ts = list(
            filter(
                lambda x: x["id"] == self.t["id"],
                challonge.tournaments.index(state="in_progress"),
            )
        )
        assert ts == []

    def test_index_filter_by_created(self):
        ts = challonge.tournaments.index(
            created_after=datetime.datetime.now().date() - datetime.timedelta(days=1)
        )
        assert self.t["id"] in map(lambda x: x["id"], ts)

    def test_show(self):
        assert challonge.tournaments.show(self.t["id"]) == self.t

    def test_update_name(self):
        t = challonge.tournaments.update(self.t["id"], name="Test!")
        assert t["name"] == "Test!"
        assert t["updated_at"] >= self.t["updated_at"]

        t.pop("name")
        t.pop("updated_at")
        self.t.pop("name")
        self.t.pop("updated_at")
        assert t == self.t

    def test_update_private(self):
        challonge.tournaments.update(self.t["id"], private=True)
        assert challonge.tournaments.show(self.t["id"])["private"] is True

    def test_update_type(self):
        challonge.tournaments.update(self.t["id"], tournament_type="round robin")
        assert (
            challonge.tournaments.show(self.t["id"])["tournament_type"] == "round robin"
        )

    def test_open(self):
        challonge.tournaments.update(self.t["id"], prediction_method=1)
        challonge.participants.create(self.t["id"], "#1")
        challonge.participants.create(self.t["id"], "#2")
        challonge.tournaments.open_for_predictions(self.t["id"])
        assert (
            challonge.tournaments.show(self.t["id"])["state"] == "accepting_predictions"
        )

    def test_start(self):
        with pytest.raises(challonge.ChallongeException):
            challonge.tournaments.start(self.t["id"])

        assert self.t["started_at"] is None

        challonge.participants.create(self.t["id"], "#1")
        challonge.participants.create(self.t["id"], "#2")
        challonge.tournaments.start(self.t["id"])
        assert challonge.tournaments.show(self.t["id"])["started_at"] is not None

    def test_finalize(self):
        challonge.participants.create(self.t["id"], "#1")
        challonge.participants.create(self.t["id"], "#2")
        challonge.tournaments.start(self.t["id"])

        ms = challonge.matches.index(self.t["id"])
        assert ms[0]["state"] == "open"

        challonge.matches.update(
            self.t["id"],
            ms[0]["id"],
            scores_csv="3-2,4-1,2-2",
            winner_id=ms[0]["player1_id"],
        )
        challonge.tournaments.finalize(self.t["id"])
        assert challonge.tournaments.show(self.t["id"])["completed_at"] is not None

    def test_reset(self):
        challonge.participants.create(self.t["id"], "#1")
        challonge.participants.create(self.t["id"], "#2")
        challonge.tournaments.start(self.t["id"])

        with pytest.raises(challonge.ChallongeException):
            challonge.participants.create(self.t["id"], "name")

        challonge.tournaments.reset(self.t["id"])

        p = challonge.participants.create(self.t["id"], "name")
        challonge.participants.destroy(self.t["id"], p["id"])


class TestParticipants:
    @pytest.fixture(autouse=True)
    def setup(self):
        challonge.set_credentials(username, api_key)
        self.t_name = _get_random_name()
        self.ps_names = [_get_random_name(), _get_random_name()]
        self.t = challonge.tournaments.create(self.t_name, self.t_name)
        self.ps = challonge.participants.bulk_add(self.t["id"], self.ps_names)
        yield
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ps = challonge.participants.index(self.t["id"])
        assert len(ps) == 2
        assert self.ps[0] in ps
        assert self.ps[1] in ps

    def test_show(self):
        p1 = challonge.participants.show(self.t["id"], self.ps[0]["id"])
        assert p1["id"] == self.ps[0]["id"]

    def test_create(self):
        new_player = challonge.participants.create(self.t["id"], _get_random_name())
        assert challonge.participants.show(self.t["id"], new_player["id"]) == new_player

    def test_create_with_number_names(self):
        name = "".join([str(random.randint(0, 9)) for _ in range(9)])
        new_player = challonge.participants.create(self.t["id"], name)
        assert (
            challonge.participants.show(self.t["id"], new_player["id"])["name"] == name
        )

    def test_update(self):
        p1 = challonge.participants.update(self.t["id"], self.ps[0]["id"], misc="Test!")
        assert p1["misc"] == "Test!"
        assert p1["updated_at"] >= self.ps[0]["updated_at"]

        p1.pop("misc")
        p1.pop("updated_at")
        self.ps[0].pop("misc")
        self.ps[0].pop("updated_at")
        assert self.ps[0] == p1

    @pytest.mark.skip(
        reason="API issue: undo_check_in leaves checked_in=True in response"
    )
    def test_check_in_and_undo_check_in(self):
        timezone = challonge.get_timezone()
        test_date = datetime.datetime.now(tz=timezone) + datetime.timedelta(minutes=30)
        challonge.tournaments.update(
            self.t["id"], check_in_duration=30, start_at=test_date
        )

        p1 = challonge.participants.check_in(self.t["id"], self.ps[0]["id"])
        p2 = challonge.participants.check_in(self.t["id"], self.ps[1]["id"])
        assert p1["checked_in"]
        assert p2["checked_in"]

        p1 = challonge.participants.undo_check_in(self.t["id"], self.ps[0]["id"])
        p2 = challonge.participants.undo_check_in(self.t["id"], self.ps[1]["id"])
        assert not p1["checked_in"]
        assert not p2["checked_in"]

    def test_destroy_before_tournament_start(self):
        challonge.participants.destroy(self.t["id"], self.ps[0]["id"])
        assert len(challonge.participants.index(self.t["id"])) == 1

    def test_destroy_after_tournament_start(self):
        challonge.tournaments.start(self.t["id"])
        challonge.participants.destroy(self.t["id"], self.ps[1]["id"])
        assert not challonge.participants.show(self.t["id"], self.ps[1]["id"])["active"]

    def test_randomize(self):
        ps = challonge.participants.randomize(self.t["id"])
        assert isinstance(ps, list)
        assert len(ps) == len(self.ps)


class TestMatches:
    @pytest.fixture(autouse=True)
    def setup(self):
        challonge.set_credentials(username, api_key)
        self.t_name = _get_random_name()
        self.t = challonge.tournaments.create(self.t_name, self.t_name)
        self.ps = challonge.participants.bulk_add(
            self.t["id"], [_get_random_name(), _get_random_name()]
        )
        challonge.tournaments.start(self.t["id"])
        yield
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ms = challonge.matches.index(self.t["id"])
        assert len(ms) == 1
        m = ms[0]
        assert {self.ps[0]["id"], self.ps[1]["id"]} == {
            m["player1_id"],
            m["player2_id"],
        }
        assert m["state"] == "open"

    def test_show(self):
        for m in challonge.matches.index(self.t["id"]):
            assert m == challonge.matches.show(self.t["id"], m["id"])

    def test_update_reopen(self):
        m = challonge.matches.index(self.t["id"])[0]
        assert m["state"] == "open"

        m = challonge.matches.update(
            self.t["id"], m["id"], scores_csv="3-2,4-1,2-2", winner_id=m["player1_id"]
        )
        assert m["state"] == "complete"

        m = challonge.matches.reopen(self.t["id"], m["id"])
        assert m["state"] == "open"

    def test_mark_as_underway(self):
        m = challonge.matches.index(self.t["id"])[0]
        m = challonge.matches.mark_as_underway(self.t["id"], m["id"])
        assert isinstance(m["underway_at"], datetime.datetime)

    def test_unmark_as_underway(self):
        m = challonge.matches.index(self.t["id"])[0]
        challonge.matches.mark_as_underway(self.t["id"], m["id"])
        m = challonge.matches.unmark_as_underway(self.t["id"], m["id"])
        assert m["underway_at"] is None


class TestAttachments:
    @pytest.fixture(autouse=True)
    def setup(self):
        challonge.set_credentials(username, api_key)
        self.t_name = _get_random_name()
        self.t = challonge.tournaments.create(
            self.t_name, self.t_name, accept_attachments=True
        )
        self.ps = challonge.participants.bulk_add(
            self.t["id"], [_get_random_name(), _get_random_name()]
        )
        challonge.tournaments.start(self.t["id"])
        self.match = challonge.matches.index(self.t["id"])[0]
        yield
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        challonge.attachments.create(
            self.t["id"], self.match["id"], url="http://test.com"
        )
        challonge.attachments.create(
            self.t["id"], self.match["id"], url="http://test2.com"
        )
        assert len(challonge.attachments.index(self.t["id"], self.match["id"])) == 2

    def test_create_url(self):
        a = challonge.attachments.create(
            self.t["id"], self.match["id"], url="http://test.com"
        )
        assert a["url"] == "http://test.com"

    def test_create_description(self):
        a = challonge.attachments.create(
            self.t["id"], self.match["id"], description="test text!"
        )
        assert a["description"] == "test text!"

    def test_create_url_with_description(self):
        a = challonge.attachments.create(
            self.t["id"],
            self.match["id"],
            url="http://test.com",
            description="just a test",
        )
        assert a["url"] == "http://test.com"
        assert a["description"] == "just a test"

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_create_file(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = challonge.attachments.create(self.t["id"], self.match["id"], asset=image)
        a2 = challonge.attachments.show(self.t["id"], self.match["id"], a1["id"])
        assert a1["asset"] == a2["asset"]

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_create_file_with_description(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = challonge.attachments.create(
            self.t["id"], self.match["id"], asset=image, description="just a test"
        )
        a2 = challonge.attachments.show(self.t["id"], self.match["id"], a1["id"])
        assert a1["asset"] == a2["asset"]

    def test_update_url(self):
        a = challonge.attachments.create(
            self.t["id"], self.match["id"], url="http://test.com"
        )
        a = challonge.attachments.update(
            self.t["id"], self.match["id"], a["id"], url="https://newtest.com"
        )
        assert a["url"] == "https://newtest.com"

    def test_update_description(self):
        a = challonge.attachments.create(
            self.t["id"], self.match["id"], description="test text!"
        )
        a = challonge.attachments.update(
            self.t["id"],
            self.match["id"],
            a["id"],
            description="This is an updated test!",
        )
        assert a["description"] == "This is an updated test!"

    def test_update_url_with_description(self):
        a = challonge.attachments.create(
            self.t["id"],
            self.match["id"],
            url="http://test.com",
            description="hello there!",
        )
        a = challonge.attachments.update(
            self.t["id"],
            self.match["id"],
            a["id"],
            url="http://newtest.com",
            description="added a new url!",
        )
        assert a["url"] == "http://newtest.com"
        assert a["description"] == "added a new url!"

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_update_file(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = challonge.attachments.create(self.t["id"], self.match["id"], asset=image)
        image = httpx.get("https://picsum.photos/200/300")
        a2 = challonge.attachments.update(
            self.t["id"], self.match["id"], a1["id"], asset=image
        )
        assert a1["asset"] != a2["asset"]

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_update_file_with_description(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = challonge.attachments.create(
            self.t["id"], self.match["id"], asset=image, description="just a test"
        )
        image = httpx.get("https://picsum.photos/200/300")
        a2 = challonge.attachments.update(
            self.t["id"],
            self.match["id"],
            a1["id"],
            asset=image,
            description="just a second test",
        )
        assert a1["asset"] != a2["asset"]
        assert a1["description"] != a2["description"]

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_update_file_only_description(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = challonge.attachments.create(
            self.t["id"], self.match["id"], asset=image, description="just a test"
        )
        image = httpx.get("https://picsum.photos/200/300")
        a2 = challonge.attachments.update(
            self.t["id"], self.match["id"], a1["id"], description="just a second test"
        )
        assert a1["asset"] == a2["asset"]
        assert a1["description"] != a2["description"]

    def test_destroy(self):
        a = challonge.attachments.create(
            self.t["id"],
            self.match["id"],
            url="http://test.com",
            description="just a test",
        )
        challonge.attachments.destroy(self.t["id"], self.match["id"], a["id"])
        assert challonge.attachments.index(self.t["id"], self.match["id"]) == []
