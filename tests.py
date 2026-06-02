import dataclasses
import datetime
import os
import random
import string

import httpx
import pytest
import pytest_asyncio
import tzlocal

from challonge import AsyncClient, ChallongeException, Client

username = os.environ.get("CHALLONGE_USER")
api_key = os.environ.get("CHALLONGE_KEY")


def _get_random_name():
    return "pychal_" + "".join(
        random.choice(string.ascii_lowercase) for _ in range(0, 15)
    )


class TestAPI:
    def test_credentials_stored(self):
        with Client(user="testuser", api_key="testkey") as client:
            assert client._user == "testuser"
            assert client._api_key == "testkey"

    def test_default_timezone(self):
        with Client(user=username, api_key=api_key) as client:
            assert client._tz == tzlocal.get_localzone()

    def test_custom_timezone(self):
        with Client(user=username, api_key=api_key, timezone="Asia/Seoul") as client:
            assert str(client._tz) == "Asia/Seoul"

    def test_context_manager(self):
        with Client(user=username, api_key=api_key) as client:
            result = client.tournaments.index()
        assert isinstance(result, list)


class TestTournaments:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client(user=username, api_key=api_key)
        self.random_name = _get_random_name()
        self.t = self.client.tournaments.create(self.random_name, self.random_name)
        yield
        self.client.tournaments.destroy(self.t.id)
        self.client.close()

    def test_index(self):
        ts = list(filter(lambda x: x.id == self.t.id, self.client.tournaments.index()))
        assert len(ts) == 1
        assert self.t == ts[0]

    def test_index_filter_by_state(self):
        ts = list(
            filter(
                lambda x: x.id == self.t.id,
                self.client.tournaments.index(state="pending"),
            )
        )
        assert len(ts) == 1
        assert self.t == ts[0]

        ts = list(
            filter(
                lambda x: x.id == self.t.id,
                self.client.tournaments.index(state="in_progress"),
            )
        )
        assert ts == []

    def test_index_filter_by_created(self):
        ts = self.client.tournaments.index(
            created_after=datetime.datetime.now().date() - datetime.timedelta(days=1)
        )
        assert self.t.id in [x.id for x in ts]

    def test_show(self):
        assert self.client.tournaments.show(self.t.id) == self.t

    def test_update_name(self):
        t = self.client.tournaments.update(self.t.id, name="Test!")
        assert t.name == "Test!"
        assert t.updated_at >= self.t.updated_at
        assert (
            dataclasses.replace(t, name=self.t.name, updated_at=self.t.updated_at)
            == self.t
        )

    def test_update_private(self):
        self.client.tournaments.update(self.t.id, private=True)
        assert self.client.tournaments.show(self.t.id).private is True

    def test_update_type(self):
        self.client.tournaments.update(self.t.id, tournament_type="round robin")
        assert self.client.tournaments.show(self.t.id).tournament_type == "round robin"

    def test_open(self):
        self.client.tournaments.update(self.t.id, prediction_method=1)
        self.client.participants.create(self.t.id, "#1")
        self.client.participants.create(self.t.id, "#2")
        self.client.tournaments.open_for_predictions(self.t.id)
        assert self.client.tournaments.show(self.t.id).state == "accepting_predictions"

    def test_start(self):
        with pytest.raises(ChallongeException):
            self.client.tournaments.start(self.t.id)

        assert self.t.started_at is None

        self.client.participants.create(self.t.id, "#1")
        self.client.participants.create(self.t.id, "#2")
        self.client.tournaments.start(self.t.id)
        assert self.client.tournaments.show(self.t.id).started_at is not None

    def test_finalize(self):
        self.client.participants.create(self.t.id, "#1")
        self.client.participants.create(self.t.id, "#2")
        self.client.tournaments.start(self.t.id)

        ms = self.client.matches.index(self.t.id)
        assert ms[0].state == "open"

        self.client.matches.update(
            self.t.id,
            ms[0].id,
            scores_csv="3-2,4-1,2-2",
            winner_id=ms[0].player1_id,
        )
        self.client.tournaments.finalize(self.t.id)
        assert self.client.tournaments.show(self.t.id).completed_at is not None

    def test_reset(self):
        self.client.participants.create(self.t.id, "#1")
        self.client.participants.create(self.t.id, "#2")
        self.client.tournaments.start(self.t.id)

        with pytest.raises(ChallongeException):
            self.client.participants.create(self.t.id, "name")

        self.client.tournaments.reset(self.t.id)

        p = self.client.participants.create(self.t.id, "name")
        self.client.participants.destroy(self.t.id, p.id)


class TestParticipants:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client(user=username, api_key=api_key)
        self.t_name = _get_random_name()
        self.ps_names = [_get_random_name(), _get_random_name()]
        self.t = self.client.tournaments.create(self.t_name, self.t_name)
        self.ps = self.client.participants.bulk_add(self.t.id, self.ps_names)
        yield
        self.client.tournaments.destroy(self.t.id)
        self.client.close()

    def test_index(self):
        ps = self.client.participants.index(self.t.id)
        assert len(ps) == 2
        assert self.ps[0] in ps
        assert self.ps[1] in ps

    def test_show(self):
        p1 = self.client.participants.show(self.t.id, self.ps[0].id)
        assert p1.id == self.ps[0].id

    def test_create(self):
        new_player = self.client.participants.create(self.t.id, _get_random_name())
        assert self.client.participants.show(self.t.id, new_player.id) == new_player

    def test_create_with_number_names(self):
        name = "".join([str(random.randint(0, 9)) for _ in range(9)])
        new_player = self.client.participants.create(self.t.id, name)
        assert self.client.participants.show(self.t.id, new_player.id).name == name

    def test_update(self):
        p1 = self.client.participants.update(self.t.id, self.ps[0].id, misc="Test!")
        assert p1.misc == "Test!"
        assert p1.updated_at >= self.ps[0].updated_at
        assert (
            dataclasses.replace(
                p1, misc=self.ps[0].misc, updated_at=self.ps[0].updated_at
            )
            == self.ps[0]
        )

    @pytest.mark.skip(
        reason="API issue: undo_check_in leaves checked_in=True in response"
    )
    def test_check_in_and_undo_check_in(self):
        timezone = self.client._tz
        test_date = datetime.datetime.now(tz=timezone) + datetime.timedelta(minutes=30)
        self.client.tournaments.update(
            self.t.id, check_in_duration=30, start_at=test_date
        )

        p1 = self.client.participants.check_in(self.t.id, self.ps[0].id)
        p2 = self.client.participants.check_in(self.t.id, self.ps[1].id)
        assert p1.checked_in
        assert p2.checked_in

        p1 = self.client.participants.undo_check_in(self.t.id, self.ps[0].id)
        p2 = self.client.participants.undo_check_in(self.t.id, self.ps[1].id)
        assert not p1.checked_in
        assert not p2.checked_in

    def test_destroy_before_tournament_start(self):
        self.client.participants.destroy(self.t.id, self.ps[0].id)
        assert len(self.client.participants.index(self.t.id)) == 1

    def test_destroy_after_tournament_start(self):
        self.client.tournaments.start(self.t.id)
        self.client.participants.destroy(self.t.id, self.ps[1].id)
        assert not self.client.participants.show(self.t.id, self.ps[1].id).active

    def test_randomize(self):
        ps = self.client.participants.randomize(self.t.id)
        assert isinstance(ps, list)
        assert len(ps) == len(self.ps)


class TestMatches:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client(user=username, api_key=api_key)
        self.t_name = _get_random_name()
        self.t = self.client.tournaments.create(self.t_name, self.t_name)
        self.ps = self.client.participants.bulk_add(
            self.t.id, [_get_random_name(), _get_random_name()]
        )
        self.client.tournaments.start(self.t.id)
        yield
        self.client.tournaments.destroy(self.t.id)
        self.client.close()

    def test_index(self):
        ms = self.client.matches.index(self.t.id)
        assert len(ms) == 1
        m = ms[0]
        assert {self.ps[0].id, self.ps[1].id} == {m.player1_id, m.player2_id}
        assert m.state == "open"

    def test_show(self):
        for m in self.client.matches.index(self.t.id):
            assert m == self.client.matches.show(self.t.id, m.id)

    def test_update_reopen(self):
        m = self.client.matches.index(self.t.id)[0]
        assert m.state == "open"

        m = self.client.matches.update(
            self.t.id, m.id, scores_csv="3-2,4-1,2-2", winner_id=m.player1_id
        )
        assert m.state == "complete"

        m = self.client.matches.reopen(self.t.id, m.id)
        assert m.state == "open"

    def test_mark_as_underway(self):
        m = self.client.matches.index(self.t.id)[0]
        m = self.client.matches.mark_as_underway(self.t.id, m.id)
        assert isinstance(m.underway_at, datetime.datetime)

    def test_unmark_as_underway(self):
        m = self.client.matches.index(self.t.id)[0]
        self.client.matches.mark_as_underway(self.t.id, m.id)
        m = self.client.matches.unmark_as_underway(self.t.id, m.id)
        assert m.underway_at is None


class TestAttachments:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client(user=username, api_key=api_key)
        self.t_name = _get_random_name()
        self.t = self.client.tournaments.create(
            self.t_name, self.t_name, accept_attachments=True
        )
        self.ps = self.client.participants.bulk_add(
            self.t.id, [_get_random_name(), _get_random_name()]
        )
        self.client.tournaments.start(self.t.id)
        self.match = self.client.matches.index(self.t.id)[0]
        yield
        self.client.tournaments.destroy(self.t.id)
        self.client.close()

    def test_index(self):
        self.client.attachments.create(self.t.id, self.match.id, url="http://test.com")
        self.client.attachments.create(self.t.id, self.match.id, url="http://test2.com")
        assert len(self.client.attachments.index(self.t.id, self.match.id)) == 2

    def test_create_url(self):
        a = self.client.attachments.create(
            self.t.id, self.match.id, url="http://test.com"
        )
        assert a.url == "http://test.com"

    def test_create_description(self):
        a = self.client.attachments.create(
            self.t.id, self.match.id, description="test text!"
        )
        assert a.description == "test text!"

    def test_create_url_with_description(self):
        a = self.client.attachments.create(
            self.t.id,
            self.match.id,
            url="http://test.com",
            description="just a test",
        )
        assert a.url == "http://test.com"
        assert a.description == "just a test"

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_create_file(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = self.client.attachments.create(self.t.id, self.match.id, asset=image)
        a2 = self.client.attachments.show(self.t.id, self.match.id, a1.id)
        assert a1.asset_url == a2.asset_url

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_create_file_with_description(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = self.client.attachments.create(
            self.t.id, self.match.id, asset=image, description="just a test"
        )
        a2 = self.client.attachments.show(self.t.id, self.match.id, a1.id)
        assert a1.asset_url == a2.asset_url

    def test_update_url(self):
        a = self.client.attachments.create(
            self.t.id, self.match.id, url="http://test.com"
        )
        a = self.client.attachments.update(
            self.t.id, self.match.id, a.id, url="https://newtest.com"
        )
        assert a.url == "https://newtest.com"

    def test_update_description(self):
        a = self.client.attachments.create(
            self.t.id, self.match.id, description="test text!"
        )
        a = self.client.attachments.update(
            self.t.id, self.match.id, a.id, description="This is an updated test!"
        )
        assert a.description == "This is an updated test!"

    def test_update_url_with_description(self):
        a = self.client.attachments.create(
            self.t.id,
            self.match.id,
            url="http://test.com",
            description="hello there!",
        )
        a = self.client.attachments.update(
            self.t.id,
            self.match.id,
            a.id,
            url="http://newtest.com",
            description="added a new url!",
        )
        assert a.url == "http://newtest.com"
        assert a.description == "added a new url!"

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_update_file(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = self.client.attachments.create(self.t.id, self.match.id, asset=image)
        image = httpx.get("https://picsum.photos/200/300")
        a2 = self.client.attachments.update(
            self.t.id, self.match.id, a1.id, asset=image
        )
        assert a1.asset_url != a2.asset_url

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_update_file_with_description(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = self.client.attachments.create(
            self.t.id, self.match.id, asset=image, description="just a test"
        )
        image = httpx.get("https://picsum.photos/200/300")
        a2 = self.client.attachments.update(
            self.t.id,
            self.match.id,
            a1.id,
            asset=image,
            description="just a second test",
        )
        assert a1.asset_url != a2.asset_url
        assert a1.description != a2.description

    @pytest.mark.skip(reason="API issue: file upload returns 500")
    def test_update_file_only_description(self):
        image = httpx.get("https://picsum.photos/200/300")
        a1 = self.client.attachments.create(
            self.t.id, self.match.id, asset=image, description="just a test"
        )
        image = httpx.get("https://picsum.photos/200/300")
        a2 = self.client.attachments.update(
            self.t.id, self.match.id, a1.id, description="just a second test"
        )
        assert a1.asset_url == a2.asset_url
        assert a1.description != a2.description

    def test_destroy(self):
        a = self.client.attachments.create(
            self.t.id,
            self.match.id,
            url="http://test.com",
            description="just a test",
        )
        self.client.attachments.destroy(self.t.id, self.match.id, a.id)
        assert self.client.attachments.index(self.t.id, self.match.id) == []


class TestAsyncClient:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.client = AsyncClient(user=username, api_key=api_key)
        self.random_name = _get_random_name()
        self.t = await self.client.tournaments.create(
            self.random_name, self.random_name
        )
        yield
        await self.client.tournaments.destroy(self.t.id)
        await self.client.aclose()

    async def test_tournament_show(self):
        t = await self.client.tournaments.show(self.t.id)
        assert t.id == self.t.id
        assert t.name == self.t.name

    async def test_participant_create_and_show(self):
        p = await self.client.participants.create(self.t.id, _get_random_name())
        assert (await self.client.participants.show(self.t.id, p.id)).id == p.id

    async def test_match_index(self):
        ps_names = [_get_random_name(), _get_random_name()]
        await self.client.participants.bulk_add(self.t.id, ps_names)
        await self.client.tournaments.start(self.t.id)
        ms = await self.client.matches.index(self.t.id)
        assert len(ms) == 1
        assert ms[0].state == "open"

    async def test_attachment_create_and_destroy(self):
        t = await self.client.tournaments.create(
            _get_random_name(), _get_random_name(), accept_attachments=True
        )
        await self.client.participants.bulk_add(
            t.id, [_get_random_name(), _get_random_name()]
        )
        await self.client.tournaments.start(t.id)
        match = (await self.client.matches.index(t.id))[0]
        a = await self.client.attachments.create(t.id, match.id, url="http://test.com")
        assert a.url == "http://test.com"
        await self.client.attachments.destroy(t.id, match.id, a.id)
        assert await self.client.attachments.index(t.id, match.id) == []
        await self.client.tournaments.destroy(t.id)
