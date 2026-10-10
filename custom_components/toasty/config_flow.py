"""Set up a Toasty account using its Settings API key."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from .api import ToastyApi, ToastyAuthError, ToastyError
from .const import DOMAIN

SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))})

class ToastyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input[CONF_API_KEY].strip()
            try:
                data = await ToastyApi(async_get_clientsession(self.hass), token).snapshot()
            except ToastyAuthError:
                errors["base"] = "invalid_auth"
            except ToastyError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(data["accountId"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Toasty", data={CONF_API_KEY: token})
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input[CONF_API_KEY].strip()
            try:
                data = await ToastyApi(async_get_clientsession(self.hass), token).snapshot()
            except ToastyAuthError:
                errors["base"] = "invalid_auth"
            except ToastyError:
                errors["base"] = "cannot_connect"
            else:
                entry = self._get_reauth_entry()
                if data["accountId"] != entry.unique_id:
                    errors["base"] = "wrong_account"
                else:
                    return self.async_update_reload_and_abort(entry, data_updates={CONF_API_KEY: token})
        return self.async_show_form(step_id="reauth_confirm", data_schema=SCHEMA, errors=errors)
