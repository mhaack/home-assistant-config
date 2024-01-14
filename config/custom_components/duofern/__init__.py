import asyncio
import logging
import os
import re
from typing import Any

# from homeassistant.const import 'serial_port', 'config_file', 'code'
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry

from pyduofern.duofern_stick import DuofernStickThreaded

from custom_components.duofern.domain_data import getDuofernStick, setupDomainData

# found advice in the homeassistant creating components manual
# https://home-assistant.io/developers/creating_components/
# Import the device class from the component that you want to support

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['pyduofern==0.34.1']

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, DUOFERN_COMPONENTS
from .domain_data import _getData
from custom_components.duofern.domain_data import getDuofernStick, isDeviceSetUp, saveDeviceAsSetUp, unsetupDevice

from homeassistant.helpers.device_registry import DeviceEntry

SERVICES = ['start_pairing', 'start_unpairing', 'clean_config', 'dump_device_state', 'ask_for_update',
            'set_update_interval']

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({
    vol.Optional('serial_port',
                 default="/dev/serial/by-id/usb-Rademacher_DuoFern_USB-Stick_WR04ZFP4-if00-port0"): cv.string,
    vol.Optional('config_file', default=os.path.join(os.path.dirname(__file__), "../../duofern.json")): cv.string,
    # config file: default to homeassistant config directory (assuming this is a custom component)
    vol.Optional('code', default="0000"): cv.string,
}),
}, extra=vol.ALLOW_EXTRA)


async def async_remove_config_entry_device(
        hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    stick = getDuofernStick(hass)
    if device_entry.name in stick.duofern_parser.modules["by_code"]:
        del stick.duofern_parser.modules["by_code"][device_entry.name]
    stick.config['devices'] = [dev for dev in stick.config['devices'] if dev['id'] != device_entry.name]
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload deCONZ config entry."""

    stick = getDuofernStick(hass)
    stick.sync_devices()
    stick.stop()
    try:
        stick.serial_connection.close()
    except:
        _LOGGER.exception("closing serial connection failed")

    await asyncio.sleep(0.5)



    for duofernDevice in stick.config['devices']:
        _LOGGER.info(f"unsetting up device {duofernDevice}")
        duofernId: str = duofernDevice['id']
        if not isDeviceSetUp(hass, duofernId):
            continue
        _LOGGER.info(f"unsetting up device {duofernDevice}")
        unsetupDevice(hass, duofernId)

    for component in DUOFERN_COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(config_entry, component)
        )


    newstick = DuofernStickThreaded(serial_port=stick.port, system_code=stick.system_code,
                                    config_file_json=stick.config_file,
                                    ephemeral=False)
    newstick.start()
    hass.data[DOMAIN]['stick'] = newstick
    del stick

    return True


@callback
def async_unload_services(hass: HomeAssistant) -> None:
    for service in SERVICES:
        hass.services.async_remove(DOMAIN, service)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the duofern stick for communicating with the duofern devices via entities"""
    configEntries = hass.config_entries.async_entries(DOMAIN)
    if len(configEntries) == 0:
        _LOGGER.error("Expected one config entry from configuration flow, got less")
        return False

    if len(configEntries) > 1:
        _LOGGER.error("Expected one config entry from configuration flow, got more")
        return False

    serial_port = configEntries[0].data['serial_port']
    code = configEntries[0].data['code']
    configfile = configEntries[0].data['config_file']

    stick = DuofernStickThreaded(serial_port=serial_port, system_code=code, config_file_json=configfile,
                                 ephemeral=False)

    _registerServices(hass, stick, configEntries[0])
    _registerUpdateHassFromStickCallback(hass, stick)
    _registerStartStickHook(hass, stick)

    setupDomainData(hass, stick)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the Duofern Config entries (entities, devices, etc...)"""
    for component in DUOFERN_COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


def _registerStartStickHook(hass: HomeAssistant, stick: DuofernStickThreaded) -> None:
    def started_callback(event: Any) -> None:
        stick.start()  # Start the stick when ha is ready

    hass.bus.listen("homeassistant_started", started_callback)


def _registerUpdateHassFromStickCallback(hass: HomeAssistant, stick: DuofernStickThreaded) -> None:
    def update_callback(id: str | None, key: Any, value: Any) -> None:
        if id is not None:
            try:
                _LOGGER.info(f"Updatecallback for {id}")
                device = hass.data[DOMAIN]['devices'][id]  # Get device by id
                if device.enabled:
                    try:
                        device.schedule_update_ha_state(True)  # Trigger update on the updated entity
                    except AssertionError:
                        _LOGGER.info("Update callback called before HA is ready")  # Trying to update before HA is ready
            except KeyError:
                _LOGGER.info("Update callback called on unknown device id")  # Ignore invalid device ids

    stick.add_updates_callback(update_callback)


def _registerServices(hass: HomeAssistant, stick: DuofernStickThreaded, entry: ConfigEntry) -> None:
    def start_pairing(call: ServiceCall) -> None:
        _LOGGER.warning("start pairing")
        getDuofernStick(hass).pair(call.data.get('timeout', 60))

    def start_unpairing(call: ServiceCall) -> None:
        _LOGGER.warning("start pairing")
        getDuofernStick(hass).unpair(call.data.get('timeout', 60))

    def sync_devices(call: ServiceCall) -> None:
        stick.sync_devices()

    def dump_device_state(call: ServiceCall) -> None:
        _LOGGER.warning(getDuofernStick(hass).duofern_parser.modules)

    def clean_config(call: ServiceCall) -> None:
        stick.clean_config()
        stick.duofern_parser.modules = {'by_code': {}}
        stick.sync_devices()

    def ask_for_update(call: ServiceCall) -> None:
        device_id = None

        def get_device_id(hass_entity_id):
            for ent in hass.data[DOMAIN]['devices'].values():
                if ent.entity_id == hass_entity_id:
                    return ent._duofernId
            return None

        try:
            get_all = call.data.get('all', None)
            hass_device_id = call.data.get('device_id', None)
            if get_all:
                _LOGGER.info("Asking all devices for update")
                device_ids = hass.data[DOMAIN]['stick'].duofern_parser.modules['by_code'].keys()
            else:
                _LOGGER.info("Asking specific devices for update")
                device_ids = [get_device_id(i) for i in hass_device_id]
        except Exception:
            _LOGGER.exception(
                f"Exception while getting device id {call}, {call.data}, i know {hass.data[DOMAIN]['deviceByHassId']}, fyi deviceByID is {hass.data[DOMAIN]['devices']}")
            for id, dev in hass.data[DOMAIN]['deviceByHassId'].items():
                _LOGGER.warning(f"{id}, {dev.__dict__}")
            raise
        if device_ids is None:
            _LOGGER.warning(f"device_id missing from call {call.data}")
            return
        _LOGGER.info(f"Updating these devices {' '.join(device_ids)}")
        if not device_ids or all([i is None for i in device_ids]):
            _LOGGER.warning("Found no valid device ids???")
        for device_id in device_ids:
            if device_id is not None:
                if device_id not in hass.data[DOMAIN]['stick'].duofern_parser.modules['by_code']:
                    _LOGGER.warning(
                        f"{device_id} is not a valid duofern device, I only know {hass.data[DOMAIN]['stick'].duofern_parser.modules['by_code'].keys()}. Gonna handle the other devices in {device_ids} though.")
                    continue
                _LOGGER.info(f"asking {device_id} for update")
                getDuofernStick(hass).command(device_id, 'getStatus')

    def set_update_interval(call: ServiceCall) -> None:
        try:
            period_minutes = call.data.get('period_minutes', None)
            if period_minutes == int(0):
                period_minutes = None
                _LOGGER.warning("set period_minutes to 0 - no updates will be triggered automatically")
        except Exception:
            _LOGGER.warning("something went wrong while reading period from parameters")
            return
        getDuofernStick(hass).updating_interval = period_minutes

    PAIRING_SCHEMA = vol.Schema({
        vol.Optional('timeout', default=30): cv.positive_int,
    })

    UPDATE_SCHEMA = vol.Schema({
        vol.Optional('all', default=False): bool,
        vol.Optional('device_id', default=list, ): list,
    })

    UPDATE_INTERVAL_SCHEMA = vol.Schema({
        vol.Optional('period_minutes', default=5): cv.positive_int,
    })

    hass.services.register(DOMAIN, 'start_pairing', start_pairing, PAIRING_SCHEMA)
    hass.services.register(DOMAIN, 'start_unpairing', start_unpairing, PAIRING_SCHEMA)
    hass.services.register(DOMAIN, 'sync_devices', sync_devices)
    #hass.services.register(DOMAIN, 'clean_config', clean_config)
    hass.services.register(DOMAIN, 'dump_device_state', dump_device_state)
    hass.services.register(DOMAIN, 'ask_for_update', ask_for_update, UPDATE_SCHEMA)
    hass.services.register(DOMAIN, 'set_update_interval', set_update_interval, UPDATE_INTERVAL_SCHEMA)
