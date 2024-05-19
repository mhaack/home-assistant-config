"""Sensor support for Mercedes cars with Mercedes ME.

For more details about this component, please refer to the documentation at
https://github.com/ReneNulschDE/mbapi2020/
"""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import RestoreSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MercedesMeEntity
from .const import (
    CONF_FT_DISABLE_CAPABILITY_CHECK,
    DOMAIN,
    LOGGER,
    SENSORS,
    SENSORS_POLL,
    DefaultValueModeType,
    SensorConfigFields as scf,
)
from .coordinator import MBAPI2020DataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setups sensor platform."""

    coordinator: MBAPI2020DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    if not coordinator.client.cars:
        LOGGER.info("No Cars found.")
        return

    sensor_list = []
    for car in coordinator.client.cars.values():
        for key, value in sorted(SENSORS.items()):
            if (
                value[scf.CAPABILITIES_LIST.value] is None
                or config_entry.options.get(CONF_FT_DISABLE_CAPABILITY_CHECK, False) is True
                or car.features.get(value[scf.CAPABILITIES_LIST.value], False) is True
            ):
                device = MercedesMESensor(
                    internal_name=key,
                    sensor_config=value,
                    vin=car.finorvin,
                    coordinator=coordinator,
                )
                if device.device_retrieval_status() in ["VALID", "NOT_RECEIVED"] or (
                    value[scf.DEFAULT_VALUE_MODE.value] is not None
                    and value[scf.DEFAULT_VALUE_MODE.value] != DefaultValueModeType.NONE
                ):
                    sensor_list.append(device)

        for key, value in sorted(SENSORS_POLL.items()):
            if (
                value[scf.CAPABILITIES_LIST.value] is None
                or config_entry.options.get(CONF_FT_DISABLE_CAPABILITY_CHECK, False) is True
                or car.features.get(value[scf.CAPABILITIES_LIST.value], False) is True
            ):
                device = MercedesMESensorPoll(
                    internal_name=key,
                    sensor_config=value,
                    vin=car.finorvin,
                    coordinator=coordinator,
                    should_poll=True,
                )
                if device.device_retrieval_status() in ["VALID", "NOT_RECEIVED"] or (
                    value[scf.DEFAULT_VALUE_MODE.value] is not None
                    and value[scf.DEFAULT_VALUE_MODE.value] != DefaultValueModeType.NONE
                ):
                    sensor_list.append(device)

    async_add_entities(sensor_list, True)


class MercedesMESensor(MercedesMeEntity, RestoreSensor):
    """Representation of a Sensor."""

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the state."""
        return self.state

    @property
    def state(self):
        """Return the state of the sensor."""

        if self.device_retrieval_status() == "NOT_RECEIVED":
            return "NOT_RECEIVED"

        if self._internal_name == "lastParkEvent":
            # try:
            return datetime.fromtimestamp(int(self._state))
        # finally:
        #     return None

        return self._state

    # async def async_added_to_hass(self) -> None:
    #     """Call when entity about to be added to Home Assistant."""
    #     await super().async_added_to_hass()
    #     # __init__ will set self._state to self._initial, only override
    #     # if needed.

    #     if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
    #         self._state = last_sensor_data.native_value


class MercedesMESensorPoll(MercedesMeEntity, RestoreSensor):
    """Representation of a Sensor."""

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the state."""
        return self.state

    @property
    def state(self):
        """Return the state of the sensor."""

        if self.device_retrieval_status() == "NOT_RECEIVED":
            return "NOT_RECEIVED"

        return self._state

    # async def async_added_to_hass(self) -> None:
    #     """Call when entity about to be added to Home Assistant."""
    #     await super().async_added_to_hass()
    #     # __init__ will set self._state to self._initial, only override
    #     # if needed.
    #     if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
    #         self._state = last_sensor_data.native_value

    # async def async_update(self):
    #     """Get the latest data and updates the states."""
    #     LOGGER.debug("Updating %s", self._internal_name)

    #     await self._coordinator.client.update_poll_states(self._vin)

    #     self._state = self._get_car_value(self._feature_name, self._object_name, self._attrib_name, "error")
