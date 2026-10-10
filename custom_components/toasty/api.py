"""Small async client for the account-scoped Toasty API."""
import asyncio
from urllib.parse import quote
import aiohttp
from .const import BASE_URL

class ToastyError(Exception):
    """The Toasty request failed."""

class ToastyAuthError(ToastyError):
    """The key was rejected."""

class ToastyApi:
    def __init__(self, session: aiohttp.ClientSession, token: str):
        self.session = session
        self._token = token

    async def request(self, method: str, path: str, **kwargs):
        try:
            async with asyncio.timeout(15):
                async with self.session.request(method, BASE_URL + "/api/v1/" + path,
                    headers={"Authorization": "Bearer " + self._token}, **kwargs) as response:
                    if response.status in (401, 403):
                        raise ToastyAuthError("API key rejected")
                    if response.status != 200:
                        raise ToastyError(f"Toasty returned HTTP {response.status}")
                    return await response.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise ToastyError("Unable to reach Toasty") from err

    async def snapshot(self):
        data = await self.request("GET", "screens")
        if not isinstance(data, dict) or not isinstance(data.get("accountId"), str) or not isinstance(data.get("screens"), list) or not isinstance(data.get("applets"), list):
            raise ToastyError("Invalid Toasty response")
        return data

    async def set_applet(self, screen_id: str, applet: str):
        return await self.request("POST", "screens/" + quote(screen_id, safe=""), json={"activeApp": applet})
