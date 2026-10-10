"""Toasty account integration."""
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import ToastyApi
from .coordinator import ToastyCoordinator

PLATFORMS = [Platform.SELECT]

async def async_setup_entry(hass, entry):
    coordinator = ToastyCoordinator(hass, entry, ToastyApi(async_get_clientsession(hass), entry.data[CONF_API_KEY]))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
