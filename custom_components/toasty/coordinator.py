"""One shared refresh discovers and updates all screens."""
from datetime import timedelta
import logging
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import ToastyAuthError, ToastyError
from .const import DOMAIN

class ToastyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, api):
        super().__init__(hass, logging.getLogger(__name__), name=DOMAIN,
            config_entry=entry, update_interval=timedelta(seconds=30), always_update=False)
        self.api = api

    async def _async_update_data(self):
        try:
            return await self.api.snapshot()
        except ToastyAuthError as err:
            raise ConfigEntryAuthFailed("Toasty API key was revoked or replaced") from err
        except ToastyError as err:
            raise UpdateFailed(str(err)) from err
