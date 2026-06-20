"""Constants for the Stateless AC Infrared integration."""

from homeassistant.const import UnitOfTemperature

from .remotes.yae1k2 import YAE1K2Remote

DOMAIN = "stateless_ac_infrared"

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_REMOTE_TYPE = "remote_type"
CONF_TEMP_SENSOR = "temp_sensor"
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_TEMP_STEP = "temp_step"

DEFAULT_MIN_TEMP = 60.0
DEFAULT_MAX_TEMP = 85.0
DEFAULT_MIN_TEMP_C = 16.0
DEFAULT_MAX_TEMP_C = 30.0
DEFAULT_TEMP_STEP = "step_1"
DEFAULT_TEMPERATURE_UNIT = UnitOfTemperature.FAHRENHEIT

SERVICE_CALIBRATE = "calibrate"
ATTR_TARGET_TEMPERATURE = "target_temperature"

TEMP_STEPS = {"step_0_1": 0.1, "step_0_5": 0.5, "step_1": 1.0}

SUPPORTED_REMOTES = {
    "yae1k2": YAE1K2Remote,
    # "yae1k1": YAE1K1Remote,
    # "test": TestRemote
}
