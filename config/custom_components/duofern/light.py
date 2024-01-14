import logging
import math

# from homeassistant.const import 'serial_port', 'config_file', 'code'
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol
# found advice in the homeassistant creating components manual
# https://home-assistant.io/developers/creating_components/
# Import the device class from the component that you want to support
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA, SUPPORT_BRIGHTNESS, ATTR_BRIGHTNESS

from homeassistant.core import HomeAssistant

from pyduofern.duofern_stick import DuofernStickThreaded

# Home Assistant depends on 3rd party packages for API specific code.

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
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
    """Setup the Awesome Light platform."""

    # Assign configuration variables. The configuration check takes care they are
    # present.

    stick: DuofernStickThreaded = hass.data["duofern"]['stick']

    # Add devices
    for device in stick.config['devices']:
        if device['id'].startswith('46') or device['id'].startswith('48'):
            if device['id'] in hass.data[DOMAIN]['devices'].keys():
                continue
            async_add_entities([DuofernLight(device['id'], device['name'], stick, hass)])

        if device['id'].startswith('43'):
            for channel in [1,2]:
                chanNo = "{:02x}".format(channel)
                if device['id']+chanNo in hass.data[DOMAIN]['devices'].keys():
                    continue
                async_add_entities([DuofernLight(device['id'], device['name'], stick, hass, channel=channel)])


class DuofernLight(LightEntity):
    def __init__(self, code: str, desc: str, stick: DuofernStickThreaded, hass: HomeAssistant, channel: int|None=None):
        """Initialize the light."""
        self._code = code
        self._id = code
        self._name = desc

        if channel:
          chanNo = "{:02x}".format(channel)
          self._id += chanNo
          self._name += chanNo

        self._state = None
        self._stick = stick
        self._channel = channel
        hass.data[DOMAIN]['devices'][self._id] = self

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_on(self) -> bool | None:
        try:
            state: str|None = self._stick.duofern_parser.get_state(self._code, 'state', channel=self._channel)
            return state != "off"
        except KeyError:
            return None

    @property
    def unique_id(self) -> str:
        return self._id

    @property                
    def brightness(self) -> int|None:
        if self._code.startswith("48"):
            level = self._stick.duofern_parser.get_state(self._code, 'level', channel=self._channel)
            if level == None:
                return None

            return math.ceil(int(level)/100.0*255)
        else:
            return None

    @property
    def supported_features(self) -> int:  #type: ignore #(This method uses a legacy functionality)
        if self._code.startswith("48"):
            return SUPPORT_BRIGHTNESS
        else:
            return 0

    def turn_on(self,**kwargs: int) -> None:
        if self._code.startswith("48"):
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            level = math.ceil(brightness/255.0*100)
            if ATTR_BRIGHTNESS in kwargs:
                self._stick.command(self._code, "level", level, channel=self._channel)
            else:
                self._stick.command(self._code, "on", channel=self._channel) # dim slowly up

            # this is a hotfix because currently the state is detected with delay from duofern
            self._stick.duofern_parser.update_state(self._code, 'level', str(level), channel=self._channel)
            self._stick.duofern_parser.update_state(self._code, 'state', str(level), channel=self._channel)
        else:
            self._stick.command(self._code, "on", channel=self._channel)
            # this is a hotfix because currently the state is detected with delay from duofern
            self._stick.duofern_parser.update_state(self._code, 'state', "on", channel=self._channel)

    def turn_off(self, **kwargs: None) -> None:
        self._stick.command(self._code, "off", channel=self._channel)
        # this is a hotfix because currently the state is detected with delay from duofern
        self._stick.duofern_parser.update_state(self._code, 'state', "off", channel=self._channel)

    def update(self, **kwargs: None) -> None:
        pass
