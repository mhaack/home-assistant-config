import logging
from typing import Any
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv

from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA,
    BinarySensorEntity,
    BinarySensorDeviceClass
)

from homeassistant.const import (
    ATTR_BATTERY_LEVEL
)

from pyduofern.duofern_stick import DuofernStickThreaded

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Config validation
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional('serial_port', default=None): cv.string,
    vol.Optional('config_file', default=None): cv.string,
    vol.Optional('code', default=None): cv.string,
})

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the Duofern binary sensors pltaform"""

    # Get the Duofern stick instance
    stick: DuofernStickThreaded = hass.data["duofern"]['stick']

    # Add devices
    for device in stick.config['devices']:
        if device['id'].startswith('ab'): # Check if this device is a smoke detector
            if device['id'] in hass.data[DOMAIN]['devices'].keys(): # Check if Home Assistant already has this device
                continue

            async_add_entities([DuofernSmokeDetector(device['id'], device['name'], stick, hass)]) # Add new binary sensor for smoke detectors
        if device['id'].startswith('a5'): # Check if this device is a sun sensor
            if device['id'] in hass.data[DOMAIN]['devices'].keys(): # Check if Home Assistant already has this device
                continue
            async_add_entities([DuofernSunSensor(device['id'], device['name'], stick, hass)]) # Add new binary sensor for sun sensors


class DuofernSmokeDetector(BinarySensorEntity):
    """Duofern smoke detector entity"""

    def __init__(self, code: str, desc: str, stick: DuofernStickThreaded, hass: HomeAssistant, channel: int | None =None): #type for channel is a wild guess
        """Initialize the smoke detector"""

        self._code = code
        self._id = code
        self._name = desc

        if channel:
          chanNo = "{:02x}".format(channel)
          self._id += chanNo
          self._name += chanNo

        self._state: str | None = None # Holds the state (off = clear, on = smoke detected)
        self._battery_level = None # Holds the battery level of the smoke detector
        self._stick = stick # Hold an instance of the Duofern stick
        self._channel = channel
        hass.data[DOMAIN]['devices'][self._id] = self # Add device to our domain

    @property
    def name(self) -> str:
        """Returns the name of the smoke detector"""
        return self._name

    @property
    def is_on(self) -> bool:
        """Returns the current state of the smoke detector"""
        return self._state == "on"

    @property
    def device_state_attributes(self) -> dict[str, Any|None]:
        """Return the battery level of the smoke detector"""
        return {
            ATTR_BATTERY_LEVEL: self._battery_level
        }

    @property
    def icon(self) -> str:
        """Return the icon of the smoke detector"""
        return "mdi:smoke-detector"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class smoke"""
        return BinarySensorDeviceClass.SMOKE

    @property
    def should_poll(self) -> bool:
        """Whether this entity should be polled or uses subscriptions"""
        return True # TODO: Add config option for subscriptions over polling

    @property
    def unique_id(self) -> str:
        """Return the unique id of the Duofern device"""
        return self._id

    def update(self) -> None:
        """Called right before is_on() to update the current state from the stick"""
        try:
            self._state = self._stick.duofern_parser.get_state(self._code, 'state', channel=self._channel)
        except KeyError:
            self._state = None

        try:
            self._battery_level = self._stick.duofern_parser.get_state(self._code, 'batteryLevel', channel=self._channel)
        except KeyError:
            self._battery_level = None

class DuofernSunSensor(BinarySensorEntity):
    """Duofern sun sensor entity"""

    def __init__(self, code, desc, stick, hass, channel=None):
        """Initialize the sun sensor"""

        self._code = code
        self._id = code
        self._name = desc

        if channel:
          chanNo = "{:02x}".format(channel)
          self._id += chanNo
          self._name += chanNo

        self._state: str | None = None # Holds the state (off = clear, on = smoke detected)
        self._stick = stick # Hold an instance of the Duofern stick
        self._channel = channel
        hass.data[DOMAIN]['devices'][self._id] = self # Add device to our domain

    @property
    def name(self):
        """Returns the name of the sun sensor"""
        return self._name

    @property
    def is_on(self):
        """Returns the current state of the sun sensor"""
        return self._state == "on"

    @property
    def device_state_attributes(self):
        """Return the attributes of the sun sensor"""
        attributes = {
        }

        return attributes
    @property
    def icon(self):
        """Return the icon of the sun sensor"""
        return "mdi:sun-wireless-outline"

    @property
    def device_class(self):
        """Return the device class sun sensor"""
        return BinarySensorDeviceClass.LIGHT

    @property
    def should_poll(self):
        """Whether this entity should be polled or uses subscriptions"""
        return True # TODO: Add config option for subscriptions over polling

    @property
    def unique_id(self):
        """Return the unique id of the Duofern device"""
        return self._id

    def update(self):
        """Called right before is_on() to update the current state from the stick"""
        try:
            self._state = self._stick.duofern_parser.get_state(self._code, 'state', channel=self._channel)
        except KeyError:
            self._state = None

