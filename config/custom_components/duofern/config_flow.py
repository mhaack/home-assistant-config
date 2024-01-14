import os
import glob
from typing import Any, Mapping

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for duofern."""

    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input: Mapping[str, Any]|None =None) -> FlowResult:
        errors = {}
        if user_input is not None:
            if len(user_input['code']) != 4:
                errors["base"] = "not_hex"
            else:
                try:
                    if hex(int(user_input['code'], 16)).lower() != "0x" + user_input['code'].lower():
                        errors["base"] = "not_hex"
                except ValueError:
                    errors["base"] = "not_hex"
            if not errors:
                return self.async_create_entry(
                    title='duofern', data=user_input
                )

        serialdevs = set()
        if os.path.isdir("/dev/serial/by-id"):
            serialdevs.update(set(f"/dev/serial/by-id/{d}" for d in set(os.listdir("/dev/serial/by-id/"))))

        if os.path.isdir("/dev/"):
            serialdevs.update(set(glob.glob("/dev/ttyU*")))
            serialdevs.update(set(glob.glob("/dev/ttyA*")))
            serialdevs.update(set(glob.glob("/dev/duofernstick")))

        if len(serialdevs) == 0:
            serialdevs = set(["could not find /dev/serial/by-id/, /dev/tty{U,A}* or /dev/duofernstick. Did you plug in your duofern stick correctly?"])

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required('code'): str,
                vol.Optional('serial_port',
                             default="/dev/serial/by-id/usb-Rademacher_DuoFern_USB-Stick_WR04ZFP4-if00-port0"): vol.In(serialdevs),
                vol.Optional('config_file', default=os.path.join(os.path.dirname(__file__), "../../duofern.json")): str
            }),
            errors=errors
        )
