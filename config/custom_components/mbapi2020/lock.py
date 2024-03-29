"""
Lock Support for Mercedes cars with Mercedes ME.

For more details about this component, please refer to the documentation at
https://github.com/ReneNulschDE/mbapi2020/
"""

import asyncio

from homeassistant.components.alarm_control_panel import CodeFormat
from homeassistant.components.lock import LockEntity
from homeassistant.const import ATTR_CODE
from homeassistant.helpers.restore_state import RestoreEntity

from . import MercedesMeEntity
from .const import CONF_FT_DISABLE_CAPABILITY_CHECK, CONF_PIN, DOMAIN, LOCKS, LOGGER


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the sensor platform."""

    data = hass.data[DOMAIN]

    if not data.client.cars:
        LOGGER.info("No Cars found.")
        return

    sensor_list = []
    for car in data.client.cars:

        for key, value in sorted(LOCKS.items()):
            if (
                value[5] is None
                or entry.options.get(CONF_FT_DISABLE_CAPABILITY_CHECK, False) is False
                or getattr(car.features, value[5], False) is True
            ):
                device = MercedesMELock(hass=hass, data=data, internal_name=key, sensor_config=value, vin=car.finorvin)
                sensor_list.append(device)

    async_add_entities(sensor_list, True)


class MercedesMELock(MercedesMeEntity, LockEntity, RestoreEntity):
    """Representation of a Sensor."""

    async def async_lock(self, **kwargs):
        """Lock the device."""
        old_state = self.is_locked
        LOGGER.debug("starting lock")
        self._attr_is_locking = True
        await self._data.client.doors_lock(self._vin)
        LOGGER.debug("lock initiated")

        count = 0
        while count < 30:
            if old_state == self.is_locked:
                count += 1
                LOGGER.debug("lock running %s", count)
                await asyncio.sleep(1)
            else:
                break

        self._attr_is_locking = False
        LOGGER.debug("unlock finalized %s", count)

    async def async_unlock(self, **kwargs):
        """Unlock the device."""
        old_state = self.is_locked
        LOGGER.debug("starting unlock")
        code = kwargs.get(ATTR_CODE, None)
        pin = self._data.client.config_entry.options.get(CONF_PIN, None)
        self._attr_is_unlocking = True

        if pin and pin.strip():
            await self._data.client.doors_unlock_with_pin(self._vin, pin)
        else:
            if code is None:
                LOGGER.error("Code required but none provided")
            else:
                await self._data.client.doors_unlock_with_pin(self._vin, code)

        LOGGER.debug("unlock initiated")
        count = 0
        while count < 30:
            if old_state == self.is_locked:
                count += 1
                LOGGER.debug("unlock running %s", count)
                await asyncio.sleep(1)
            else:
                break
        self._attr_is_unlocking = False
        LOGGER.debug("unlock finalized %s", count)

    @property
    def is_locked(self):
        """Return true if device is locked."""

        value = self._get_car_value(self._feature_name, self._object_name, self._attrib_name, None)
        if value and int(value) == 0:
            return True

        return False

    @property
    def code_format(self):
        """Return the required four digit code if the PIN is not set in config_entry."""

        pin = self._data.client.config_entry.options.get(CONF_PIN, None)

        if pin and pin.strip():
            # Pin is set --> we don't ask for a pin
            return None

        # Pin is not set --> we ask for a pin
        return "^\\d{4}$"
