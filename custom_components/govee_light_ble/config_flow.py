from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback

from .const import CONF_SEGMENTED, DOMAIN, DISCOVERY_NAMES, default_segmented


def _segmented_schema(default: bool) -> vol.Schema:
    return vol.Schema({vol.Required(CONF_SEGMENTED, default=default): bool})


class GoveeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return GoveeOptionsFlow()

    #dicover device
    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        self._discovery_info = discovery_info
        return await self.async_step_bluetooth_confirm()

    #manual integration
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            self._discovery_info = self._discovered_devices[address]
            return await self.async_step_bluetooth_confirm()

        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass, True):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            if not (discovery_info.name or "").startswith(DISCOVERY_NAMES):
                continue
            self._discovered_devices[address] = discovery_info

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        device_list = {}
        for address in self._discovered_devices:
            device_list[address] = self._discovered_devices[address].name
    
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ADDRESS): vol.In(device_list)}
            ),
        )

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        assert self._discovery_info is not None
        discovery_info = self._discovery_info
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title=discovery_info.name, data={
                CONF_ADDRESS: discovery_info.address.upper(),
                CONF_NAME: discovery_info.name,
                CONF_SEGMENTED: user_input[CONF_SEGMENTED]
            })

        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=_segmented_schema(default_segmented(discovery_info.name))
        )


class GoveeOptionsFlow(OptionsFlow):
    """Handle options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        default = self.config_entry.options.get(
            CONF_SEGMENTED,
            self.config_entry.data.get(
                CONF_SEGMENTED,
                default_segmented(self.config_entry.data.get(CONF_NAME)),
            ),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_segmented_schema(default)
        )
