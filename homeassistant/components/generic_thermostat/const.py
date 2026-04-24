"""Constants for the Generic Thermostat helper."""

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_DIFFUSE,
    FAN_FOCUS,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_MIDDLE,
    FAN_OFF,
    FAN_ON,
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_SLEEP,
)
from homeassistant.const import Platform

DOMAIN = "generic_thermostat"

PLATFORMS = [Platform.CLIMATE]

CONF_AC_MODE = "ac_mode"
CONF_FAN_ONLY_ALLOWED = "fan_only_allowed"
CONF_ADJUSTABLE_FAN = "adjustable_fan"
CONF_FAN_MODES = "fan_modes"
FAN_MODES = {
    FAN_ON: FAN_ON,
    FAN_OFF: FAN_OFF,
    FAN_AUTO: FAN_AUTO,
    FAN_LOW: FAN_LOW,
    FAN_MEDIUM: FAN_MEDIUM,
    FAN_HIGH: FAN_HIGH,
    FAN_MIDDLE: FAN_MIDDLE,
    FAN_FOCUS: FAN_FOCUS,
    FAN_DIFFUSE: FAN_DIFFUSE,
}
CONF_INITIAL_FAN_MODE = "initial_fan_mode"
CONF_COLD_TOLERANCE = "cold_tolerance"
CONF_HEATER = "heater"
CONF_HOT_TOLERANCE = "hot_tolerance"
CONF_MAX_TEMP = "max_temp"
CONF_MIN_DUR = "min_cycle_duration"
CONF_MAX_DUR = "max_cycle_duration"
CONF_DUR_COOLDOWN = "cycle_cooldown"
CONF_MIN_TEMP = "min_temp"
CONF_PRESETS = {
    p: f"{p}_temp"
    for p in (
        PRESET_AWAY,
        PRESET_COMFORT,
        PRESET_ECO,
        PRESET_HOME,
        PRESET_SLEEP,
        PRESET_ACTIVITY,
    )
}
CONF_SENSOR = "target_sensor"
CONF_KEEP_ALIVE = "keep_alive"
DEFAULT_TOLERANCE = 0.3
