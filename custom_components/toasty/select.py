"""An applet selector for every owned Toasty screen."""
from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .api import ToastyAuthError, ToastyError
from .const import BASE_URL, DOMAIN

PARALLEL_UPDATES = 0

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    known = set()

    @callback
    def discover():
        entities = []
        for screen in coordinator.data["screens"]:
            screen_id = screen["screenId"]
            if screen_id not in known:
                known.add(screen_id)
                entities.append(ToastyAppletSelect(coordinator, screen_id))
        if entities:
            async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))

class ToastyAppletSelect(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Applet"
    _attr_icon = "mdi:television-play"

    def __init__(self, coordinator, screen_id):
        super().__init__(coordinator)
        self.screen_id = screen_id
        self._attr_unique_id = f"{screen_id}_applet"

    @property
    def screen(self):
        return next((s for s in self.coordinator.data["screens"] if s["screenId"] == self.screen_id), None)

    @property
    def device_info(self):
        return DeviceInfo(identifiers={(DOMAIN, self.screen_id)},
            name=(self.screen or {}).get("name", "Toasty screen"), manufacturer="Toasty",
            model="Screen", configuration_url=f"{BASE_URL}/app/{self.screen_id}")

    @property
    def available(self):
        return super().available and self.screen is not None

    @property
    def options(self):
        return [a["id"] for a in self.coordinator.data["applets"]]

    @property
    def current_option(self):
        return self.screen["activeApp"] if self.screen else None

    @property
    def extra_state_attributes(self):
        return {"screen_id": self.screen_id, "applet_names": {a["id"]: a["name"] for a in self.coordinator.data["applets"]}}

    async def async_select_option(self, option):
        if option not in self.options:
            raise HomeAssistantError("Unknown Toasty applet")
        try:
            result = await self.coordinator.api.set_applet(self.screen_id, option)
        except ToastyAuthError as err:
            await self.coordinator.async_request_refresh()
            raise HomeAssistantError("Toasty API key was rejected; reauthenticate the integration") from err
        except ToastyError as err:
            raise HomeAssistantError(str(err)) from err
        data = {**self.coordinator.data, "screens": [
            {**s, "activeApp": result["activeApp"]} if s["screenId"] == self.screen_id else s
            for s in self.coordinator.data["screens"]]}
        self.coordinator.async_set_updated_data(data)
