import datetime
import logging

from typing import Literal, List, Set, cast

# from homeassistant.const import 'serial_port', 'config_file', 'code'
# found advice in the homeassistant creating components manual
# https://home-assistant.io/developers/creating_components/
# Import the device class from the component that you want to support

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from random import randint

from pyduofern.duofern_stick import DuofernStickThreaded

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature
)

from custom_components.duofern.domain_data import getDuofernStick, isDeviceSetUp, saveDeviceAsSetUp

from .const import DOMAIN

# Home Assistant depends on 3rd party packages for API specific code.

_LOGGER = logging.getLogger(__name__)

SHUTTER_IDS = {"40", "41", "42", "47", "49", "4b", "4c", "4e", "70", "61"}


def is_shutter(id: str) -> bool:
    return any([id.startswith(i) for i in SHUTTER_IDS])


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the Awesome Light platform."""

    stick = getDuofernStick(hass)

    to_add: List[DuofernShutter] = []
    for duofernDevice in stick.config['devices']:
        duofernId: str = duofernDevice['id']
        if not is_shutter(duofernId):
            _LOGGER.info("button: skipping: " + str(duofernId) + " because it is not a shutter")
            continue

        if isDeviceSetUp(hass, duofernId):
            _LOGGER.info("button: skipping: " + str(duofernId) + " because it is is already set up")
            continue

        entity = DuofernShutter(duofernId, duofernDevice['name'], stick)
        to_add.append(entity)
        saveDeviceAsSetUp(hass, entity, duofernId)

    async_add_entities(to_add)


class DuofernShutter(CoverEntity):
    """Representation of Duofern cover type device."""

    def __init__(self, duofernId: str, name: str, stick: DuofernStickThreaded):
        """Initialize the shutter."""
        self._duofernId = duofernId
        self._name = name
        self._state: int | None = None
        self._stick = stick
        self._openclose: Literal["up", "down", "stop"] = 'stop'
        self._last_update_time = datetime.datetime.now()
        self._stick.updating_interval = 5

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._duofernId

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device the entity belongs to group entities to devices"""
        return {
            "identifiers": {
                (DOMAIN, self._duofernId)
            },
            "manufacturer": "Rademacher",
            "name": self.name,
        }  # type: ignore #(We only care about a subset and DeviceInfo doesn't mark the rest as optional)

    @property
    def current_cover_position(self) -> int | None:
        """Return the display name of this cover."""
        return self._state

    @property
    def is_closed(self) -> bool | None:
        """Return true if cover is close."""
        if self._state is None:
            return None
        return self._state == 0

    @property
    def should_poll(self) -> bool:
        """Whether this entity should be polled or uses subscriptions"""
        return True  # TODO: Add config option for subscriptions over polling

    @property
    def supported_features(self) -> CoverEntityFeature:
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION | CoverEntityFeature.STOP

    @property
    def icon(self) -> str:
        if self.is_opening:
            return 'mdi:arrow-up-bold'
        if self.is_closing:
            return 'mdi:arrow-down-bold'
        if self.is_closed:
            return "mdi:window-shutter"
        else:
            return "mdi:window-shutter-open"

    def open_cover(self, **kwargs: None) -> None:
        """roll up cover"""
        self._stick.command(self._duofernId, "up")

    def close_cover(self, **kwargs: None) -> None:
        """close cover"""
        self._stick.command(self._duofernId, "down")

    def stop_cover(self, **kwargs: None) -> None:
        """stop cover"""
        self._stick.command(self._duofernId, "stop")

    @property
    def is_opening(self) -> bool:
        return self._openclose == 'up'

    @property
    def is_closing(self) -> bool:
        return self._openclose == 'down'

    def set_cover_position(self, **kwargs: int) -> None:
        """set position (100-position to make the default intuitive: 0%=closed, 100%=open"""
        position = kwargs.get(ATTR_POSITION)
        if position is None: return
        self._stick.command(self._duofernId, "position", 100 - position)

    def update(self) -> None:
        """Fetch new state data for this cover.

        This is the only method that should fetch new data for Home Assistant.

        (no new data needs to be fetched, the stick updates itsself in a thread)
        (not the best style for homeassistant, I know. I'll port to asyncio if I find the time)
        """
        _LOGGER.info("updating state")
        try:
            self._state = 100 - self._stick.duofern_parser.modules['by_code'][self._duofernId]['position']
            self._openclose = self._stick.duofern_parser.modules['by_code'][self._duofernId]['moving']
        except KeyError:
            self._state = None
        if self._stick.updating_interval is not None and \
                datetime.datetime.now() - self._last_update_time > datetime.timedelta(minutes=self._stick.updating_interval):
            self._stick.command(self._duofernId, 'getStatus')
            self._last_update_time = datetime.datetime.now() + datetime.timedelta(seconds=randint(0, 60))
        _LOGGER.info(f"{self._duofernId} state is now {self._state}")
