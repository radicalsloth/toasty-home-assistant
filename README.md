# Toasty for Home Assistant

Connect your Toasty account once and control every owned screen through Home Assistant.
This is a Toasty custom integration, not part of Home Assistant Core.

## Installation

In HACS, add `https://github.com/radicalsloth/toasty-home-assistant` as a custom repository with category **Integration**, download **Toasty**, and restart Home Assistant.

For manual installation, copy `custom_components/toasty` into your Home Assistant configuration's `custom_components` directory and restart.

Then open **Settings → Devices & services → Add integration → Toasty**. Paste the account API key from [Toasty settings](https://www.toasty.so/app/account/api). No YAML, screen IDs, or Firebase credentials are needed.

## Controls

Each screen appears as a device with an **Applet** select entity. Options are the Toasty applet IDs, including `earth`, `globe`, `fireplace`, `canopy`, and `off`. Choose `earth` for the photorealistic spinning Earth; `globe` is the glowing dot globe.

```yaml
action: select.select_option
target:
  entity_id: select.bedroom_applet
data:
  option: earth
```

Screen discovery and state refresh run together every 30 seconds. Selections made in Home Assistant update immediately after the API confirms them. New screens are discovered automatically; deleted screens become unavailable. A replaced or revoked key prompts reauthentication. Diagnostics omit API keys, account IDs, and screen details.

The integration changes content. Projector wake and app launch use separate hardware integrations such as Android TV ADB. A projector that disables networking during standby still needs another wake method.

## Development

Run API-client tests with `python -m unittest discover -s tests`. Install `aiohttp` for the tests. CI validates the integration with Home Assistant hassfest and HACS validation.
