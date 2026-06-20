"""YAE1K2 remote definitions for the Stateless AC Infrared integration."""

from infrared_protocols.codes.general_electric.yae1k2 import YAE1K2Code

from homeassistant.components.climate import FAN_HIGH, FAN_LOW, FAN_MEDIUM, HVACMode

from .remote_interface import Remote


class YAE1K2Remote(Remote):
    """Remote interface for the YAE1K2 remote."""

    HVAC_MODES = {
        HVACMode.COOL: YAE1K2Code.COOL_MODE,
        HVACMode.FAN_ONLY: YAE1K2Code.FAN_MODE,
    }
    FAN_MODES = {
        FAN_LOW: YAE1K2Code.LOW,
        FAN_MEDIUM: YAE1K2Code.MED,
        FAN_HIGH: YAE1K2Code.HIGH,
    }

    POWER_COMMAND = YAE1K2Code.POWER
    UP_COMMAND = YAE1K2Code.TEMP_UP
    DOWN_COMMAND = YAE1K2Code.TEMP_DOWN
