"""Climate platform for the Stateless AC Infrared integration."""

import asyncio
import contextlib
import logging
from typing import Any, cast

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_TEMPERATURE_UNIT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_REMOTE_TYPE,
    CONF_TEMP_SENSOR,
    CONF_TEMP_STEP,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_TEMP_STEP,
    DEFAULT_TEMPERATURE_UNIT,
    SUPPORTED_REMOTES,
    TEMP_STEPS,
)
from .entity import IrEntity
from .remotes.remote_interface import Remote

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Stateless AC Infrared climate from config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    temp_sensor: str | None = entry.data.get(CONF_TEMP_SENSOR)
    min_temp: float = entry.data.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP)
    max_temp: float = entry.data.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP)
    temp_step: float = TEMP_STEPS[entry.data.get(CONF_TEMP_STEP, DEFAULT_TEMP_STEP)]
    temperature_unit = UnitOfTemperature(
        entry.data.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT)
    )
    remote = SUPPORTED_REMOTES[entry.data[CONF_REMOTE_TYPE]]

    climate_entity = StatelessClimate(
        entry,
        infrared_entity_id,
        temp_sensor=temp_sensor,
        min_temp=min_temp,
        max_temp=max_temp,
        temp_step=temp_step,
        temperature_unit=temperature_unit,
        remote=remote,
    )
    entry.runtime_data = climate_entity
    async_add_entities([climate_entity])


class StatelessClimate(IrEntity, ClimateEntity, RestoreEntity):
    """Stateless AC Infrared climate entity."""

    _attr_name = None
    _attr_icon = "mdi:air-conditioner"
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_hvac_modes = []
    _attr_fan_modes = None
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_entity_id: str,
        *,
        temp_sensor: str | None,
        min_temp: float,
        max_temp: float,
        temp_step: float,
        temperature_unit: UnitOfTemperature,
        remote: type[Remote],
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(
            entry,
            infrared_entity_id,
            unique_id_suffix="climate",
            remote_code_class=remote,
        )
        self._remote = remote
        self._temp_sensor = temp_sensor
        self._attr_min_temp = min_temp
        self._attr_max_temp = max_temp
        self._attr_temperature_unit = temperature_unit
        self._attr_target_temperature_step = temp_step
        self._attr_precision = temp_step
        self._attr_hvac_mode = HVACMode.OFF
        self._last_active_hvac_mode = HVACMode.OFF
        if not remote.HVAC_MODES:
            raise ValueError("Remote must define HVAC_MODES")
        self._attr_hvac_modes = [HVACMode.OFF, *remote.HVAC_MODES.keys()]
        self._attr_target_temperature = min_temp
        self._last_known_hardware_setpoint = min_temp

        if remote.FAN_MODES:
            self._attr_fan_modes = list(remote.FAN_MODES.keys())
            self._attr_fan_mode = self._attr_fan_modes[0]

        if remote.SWING_MODES:
            self._attr_swing_modes = list(remote.SWING_MODES.keys())
            self._attr_swing_mode = self._attr_swing_modes[0]

        self._sync_lock = asyncio.Lock()

    async def async_added_to_hass(self) -> None:
        """Restore previous state and subscribe to sensor updates."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            if last_state.state in [m.value for m in HVACMode]:
                self._attr_hvac_mode = HVACMode(last_state.state)
            attrs = last_state.attributes
            self._attr_target_temperature = float(
                attrs.get("target_temperature", self._attr_min_temp)
            )
            if (fan_mode := attrs.get("fan_mode")) is not None:
                self._attr_fan_mode = fan_mode
            if (last_active := attrs.get("last_active_hvac_mode")) is not None:
                self._last_active_hvac_mode = HVACMode(last_active)
            if (last_hw := attrs.get("last_known_hardware_setpoint")) is not None:
                self._last_known_hardware_setpoint = float(last_hw)
            if (
                self._temp_sensor is None
                and (cur_temp := attrs.get("current_temperature")) is not None
            ):
                self._attr_current_temperature = float(cur_temp)

        if self._temp_sensor is not None:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._temp_sensor],
                    self._async_sensor_state_changed,
                )
            )
            self._update_temp_from_sensor()

    @callback
    def _async_sensor_state_changed(self, event: Any) -> None:
        """Handle temperature sensor state changes."""
        self._update_temp_from_sensor()
        self.async_write_ha_state()

    @callback
    def _update_temp_from_sensor(self) -> None:
        """Pull current temperature from the linked sensor."""
        if self._temp_sensor is None:
            return
        sensor_state = self.hass.states.get(self._temp_sensor)
        if sensor_state is not None and sensor_state.state not in (
            "unknown",
            "unavailable",
        ):
            with contextlib.suppress(ValueError):
                self._attr_current_temperature = float(sensor_state.state)

    async def _async_sync_temperature(self) -> None:
        """Synchronize the hardware setpoint with the HA target temperature."""
        async with self._sync_lock:
            temp_step = cast(float, self._attr_target_temperature_step)
            while True:
                target = self._attr_target_temperature or 0
                delta = target - self._last_known_hardware_setpoint
                delta_steps = round(delta / temp_step)
                _LOGGER.debug(
                    "[%s] Temp sync: hw_setpoint=%.1f, "
                    "target=%.1f, delta=%.4f, delta_steps=%d",
                    self.entity_id,
                    self._last_known_hardware_setpoint,
                    target,
                    delta,
                    delta_steps,
                )
                if delta_steps == 0:
                    break
                code = (
                    self._remote.UP_COMMAND
                    if delta_steps > 0
                    else self._remote.DOWN_COMMAND
                )
                _LOGGER.debug("[%s] Sending %s", self.entity_id, code.name)
                await self._send_command(code)
                self._last_known_hardware_setpoint += (
                    temp_step if delta_steps > 0 else -temp_step
                )
                self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose internal tracking values for persistence."""
        return {
            "last_active_hvac_mode": self._last_active_hvac_mode,
            "last_known_hardware_setpoint": self._last_known_hardware_setpoint,
            "target_temperature": self._attr_target_temperature,
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set a new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        _LOGGER.debug(
            "[%s] set_temperature: requested=%.1f, prev_target=%.1f, mode=%s, hw_setpoint=%.1f",
            self.entity_id,
            temperature,
            self._attr_target_temperature,
            self._attr_hvac_mode,
            self._last_known_hardware_setpoint,
        )

        self._attr_target_temperature = temperature
        self.async_write_ha_state()

        if self._attr_hvac_mode in (HVACMode.OFF, HVACMode.FAN_ONLY):
            return

        await self._async_sync_temperature()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set a new fan speed."""
        _LOGGER.debug("[%s] set_fan_mode: %s", self.entity_id, fan_mode)
        fan_code_map = self._remote.FAN_MODES or {}
        if fan_mode in fan_code_map:
            _LOGGER.debug(
                "[%s] Sending %s", self.entity_id, fan_code_map[fan_mode].name
            )
            await self._send_command(fan_code_map[fan_mode])
            self._attr_fan_mode = fan_mode
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set a new HVAC mode."""
        if hvac_mode == self._attr_hvac_mode:
            return

        current = self._attr_hvac_mode
        _LOGGER.debug(
            "[%s] set_hvac_mode: %s -> %s", self.entity_id, current, hvac_mode
        )

        if hvac_mode == HVACMode.OFF:
            _LOGGER.debug("[%s] Sending POWER (turn off)", self.entity_id)
            await self._send_command(self._remote.POWER_COMMAND)
            self._attr_hvac_mode = HVACMode.OFF
        elif current == HVACMode.OFF:
            await self._async_power_on_sequence(hvac_mode)
        else:
            # Switch between active modes
            if hvac_mode == HVACMode.COOL:
                _LOGGER.debug("[%s] Sending COOL_MODE", self.entity_id)
                if self._remote.HVAC_MODES is not None:
                    await self._send_command(self._remote.HVAC_MODES[HVACMode.COOL])
                _LOGGER.debug("[%s] Waiting 0.5s for mode switch", self.entity_id)
                await asyncio.sleep(0.5)
                await self._async_sync_temperature()
            elif hvac_mode == HVACMode.FAN_ONLY:
                _LOGGER.debug("[%s] Sending FAN_MODE", self.entity_id)
                if self._remote.HVAC_MODES is not None:
                    await self._send_command(self._remote.HVAC_MODES[HVACMode.FAN_ONLY])
            self._last_active_hvac_mode = hvac_mode
            self._attr_hvac_mode = hvac_mode

        self.async_write_ha_state()

    async def _async_power_on_sequence(self, target_mode: HVACMode) -> None:
        """Power on and synchronize AC state with HA state."""
        _LOGGER.debug(
            "[%s] Power-on sequence: target=%s, last_active=%s, target_temp=%.0f, hw_setpoint=%.0f",
            self.entity_id,
            target_mode,
            self._last_active_hvac_mode,
            self._attr_target_temperature or 0,
            self._last_known_hardware_setpoint,
        )
        _LOGGER.debug("[%s] Sending POWER", self.entity_id)
        await self._send_command(self._remote.POWER_COMMAND)
        self._attr_hvac_mode = target_mode
        self.async_write_ha_state()

        if target_mode != self._last_active_hvac_mode:
            if target_mode == HVACMode.COOL:
                _LOGGER.debug("[%s] Sending COOL_MODE (mode switch)", self.entity_id)
                if self._remote.HVAC_MODES is not None:
                    await self._send_command(self._remote.HVAC_MODES[HVACMode.COOL])
            elif target_mode == HVACMode.FAN_ONLY:
                _LOGGER.debug("[%s] Sending FAN_MODE (mode switch)", self.entity_id)
                if self._remote.HVAC_MODES is not None:
                    await self._send_command(self._remote.HVAC_MODES[HVACMode.FAN_ONLY])

        if target_mode == HVACMode.COOL:
            _LOGGER.debug("[%s] Waiting 2s for AC startup", self.entity_id)
            await asyncio.sleep(2)
            await self._async_sync_temperature()

        self._last_active_hvac_mode = target_mode
        self._attr_hvac_mode = target_mode

    async def async_turn_on(self) -> None:
        """Turn the AC on."""
        await self.async_set_hvac_mode(self._last_active_hvac_mode)

    async def async_turn_off(self) -> None:
        """Turn the AC off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_calibrate(self, target_temperature: float | None = None) -> None:
        """Calibrate by zeroing the AC then climbing to the target temperature."""
        if self._attr_hvac_mode == HVACMode.OFF:
            _LOGGER.warning(
                "Calibration requires the unit to be on; current mode is OFF"
            )
            return

        original_mode = self._attr_hvac_mode
        target = (
            target_temperature
            if target_temperature is not None
            else (self._attr_target_temperature or self._attr_min_temp)
        )

        # Switch to COOL so the AC accepts temperature commands
        _LOGGER.debug("[%s] Calibrate: sending COOL_MODE", self.entity_id)
        if self._remote.HVAC_MODES is not None:
            await self._send_command(self._remote.HVAC_MODES[HVACMode.COOL])

        # Re-send the current fan speed so it is not lost during the mode switch
        fan_code_map = self._remote.FAN_MODES or {}
        if self._attr_fan_mode in fan_code_map:
            _LOGGER.debug(
                "[%s] Calibrate: sending fan mode %s",
                self.entity_id,
                self._attr_fan_mode,
            )
            await self._send_command(fan_code_map[self._attr_fan_mode])

        # Zero phase: drive the hardware setpoint to minimum
        zero_steps = int(self._attr_max_temp - self._attr_min_temp) + 1
        _LOGGER.debug(
            "[%s] Calibrate: zeroing with %d TEMP_DOWN pulses",
            self.entity_id,
            zero_steps,
        )
        for _ in range(zero_steps):
            await self._send_command(self._remote.DOWN_COMMAND)
        self._last_known_hardware_setpoint = self._attr_min_temp

        # Climb phase: move from minimum to the desired temperature
        climb_steps = round(target - self._attr_min_temp)
        _LOGGER.debug(
            "[%s] Calibrate: climbing with %d TEMP_UP pulses to %.0f",
            self.entity_id,
            climb_steps,
            target,
        )
        for _ in range(climb_steps):
            await self._send_command(self._remote.UP_COMMAND)

        self._last_known_hardware_setpoint = target
        self._attr_target_temperature = target

        # Restore FAN_ONLY if that was the mode before calibration
        if original_mode == HVACMode.FAN_ONLY:
            _LOGGER.debug("[%s] Calibrate: restoring FAN_ONLY mode", self.entity_id)
            if self._remote.HVAC_MODES is not None:
                await self._send_command(self._remote.HVAC_MODES[HVACMode.FAN_ONLY])
            self._attr_hvac_mode = HVACMode.FAN_ONLY
            self._last_active_hvac_mode = HVACMode.FAN_ONLY
        else:
            self._attr_hvac_mode = HVACMode.COOL
            self._last_active_hvac_mode = HVACMode.COOL

        self.async_write_ha_state()
