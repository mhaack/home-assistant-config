import logging

from typing import List

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from homeassistant.components.button import ButtonEntity

from custom_components.duofern.cover import is_shutter
from pyduofern.duofern_stick import DuofernStickThreaded

from custom_components.duofern.domain_data import getDuofernStick, isDeviceSetUp, saveDeviceAsSetUp

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the Duofern cover platform."""

    stick = getDuofernStick(hass)
    alreadyAddedEntityIds = hass.data[DOMAIN]['devices'].keys()

    to_add: List[ButtonEntity] = []
    _LOGGER.info("button: all devices on stick " + str(stick.config['devices']))
    for duofernDevice in stick.config['devices']:
        duofernId: str = duofernDevice['id']
        subId = "toggleButton"
        if not is_shutter(duofernId):
            _LOGGER.info("button: skipping: " + str(duofernId) + " because it is not a shutter")
            continue

        if isDeviceSetUp(hass, duofernId, subId):
            _LOGGER.info("button: skipping: " + str(duofernId) + " because it is is already set up")
            continue

        entityId = duofernId + "_toggle"
        if entityId not in alreadyAddedEntityIds:
            button = DuofernShutterToggleButton(duofernId, stick)
            to_add.append(button)
            saveDeviceAsSetUp(hass, button, duofernId, subId)

    async_add_entities(to_add)

class DuofernShutterToggleButton(ButtonEntity):
    def __init__(self, duofernId: str, stick: DuofernStickThreaded):
        """Initialize the toggle button for the shutter."""
        self._duofernId = duofernId
        self._stick = stick

    @property
    def name(self) -> str:
        return self._duofernId + " Toggle"

    @property
    def unique_id(self) -> str:
        return self._duofernId + "_toggle"

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device the entity belongs to group entities to devices"""
        return {
            "identifiers": { 
                (DOMAIN, self._duofernId)
            }
        } #type: ignore #(We only care about a subset and DeviceInfo doesn't mark the rest as optional)

    def press(self) -> None:
        """Toggles the movement of the corresponding shutter"""
        self._stick.command(self._duofernId, "toggle")
