from zoneinfo import ZoneInfo

import tzlocal
from httpx import AsyncClient as HttpxAsyncClient
from httpx import Client as HttpxClient
from httpx import HTTPStatusError

from challonge.api import ChallongeException, _parse, _prepare_params
from challonge.attachments import AttachmentsClient
from challonge.matches import MatchesClient
from challonge.participants import ParticipantsClient
from challonge.tournaments import TournamentsClient

CHALLONGE_API_URL = "api.challonge.com/v1"


class Client:
    def __init__(self, user, api_key, *, timezone=None, user_agent="pychallonge", timeout=30.0):
        self._user = user
        self._api_key = api_key
        self._tz = ZoneInfo(timezone) if timezone else tzlocal.get_localzone()
        self._user_agent = user_agent
        self._timeout = timeout
        self._http = HttpxClient()

        self.tournaments = TournamentsClient(self)
        self.participants = ParticipantsClient(self)
        self.matches = MatchesClient(self)
        self.attachments = AttachmentsClient(self)

    def _fetch(self, method, uri, params_prefix=None, **params):
        p_params = _prepare_params(params, params_prefix)
        r_data = {"data": p_params} if method in ("POST", "PUT") else {"params": p_params}
        url = f"https://{CHALLONGE_API_URL}/{uri}.json"

        try:
            response = self._http.request(
                method, url,
                headers={"User-Agent": self._user_agent},
                auth=(self._user, self._api_key),
                timeout=self._timeout,
                **r_data,
            )
            response.raise_for_status()
        except HTTPStatusError as e:
            if e.response.status_code == 422:
                doc = e.response.json()
                if doc.get("errors"):
                    raise ChallongeException(*doc["errors"]) from e
            raise

        return response

    def _fetch_and_parse(self, method, uri, params_prefix=None, target_class=None, **params):
        response = self._fetch(method, uri, params_prefix, **params)
        return _parse(response.json(), target_class, self._tz)

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AsyncClient:
    def __init__(self, user, api_key, *, timezone=None, user_agent="pychallonge", timeout=30.0):
        self._user = user
        self._api_key = api_key
        self._tz = ZoneInfo(timezone) if timezone else tzlocal.get_localzone()
        self._user_agent = user_agent
        self._timeout = timeout
        self._http = HttpxAsyncClient()

        self.tournaments = TournamentsClient(self)
        self.participants = ParticipantsClient(self)
        self.matches = MatchesClient(self)
        self.attachments = AttachmentsClient(self)

    async def _fetch(self, method, uri, params_prefix=None, **params):
        p_params = _prepare_params(params, params_prefix)
        r_data = {"data": p_params} if method in ("POST", "PUT") else {"params": p_params}
        url = f"https://{CHALLONGE_API_URL}/{uri}.json"

        try:
            response = await self._http.request(
                method, url,
                headers={"User-Agent": self._user_agent},
                auth=(self._user, self._api_key),
                timeout=self._timeout,
                **r_data,
            )
            response.raise_for_status()
        except HTTPStatusError as e:
            if e.response.status_code == 422:
                doc = e.response.json()
                if doc.get("errors"):
                    raise ChallongeException(*doc["errors"]) from e
            raise

        return response

    async def _fetch_and_parse(self, method, uri, params_prefix=None, target_class=None, **params):
        response = await self._fetch(method, uri, params_prefix, **params)
        return _parse(response.json(), target_class, self._tz)

    async def aclose(self):
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()
