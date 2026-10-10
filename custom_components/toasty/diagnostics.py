"""Diagnostics exclude credentials and account identifiers."""
async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = entry.runtime_data
    return {"screen_count": len(coordinator.data["screens"]),
        "applet_count": len(coordinator.data["applets"]),
        "last_update_success": coordinator.last_update_success}
