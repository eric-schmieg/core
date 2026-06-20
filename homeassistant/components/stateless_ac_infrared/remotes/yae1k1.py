"""YAE1K1 remote definitions for the Stateless AC Infrared integration."""

from infrared_protocols.codes.general_electric.yae1k2 import YAE1K2Code

from homeassistant.components.climate import FAN_HIGH, FAN_LOW, HVACMode

from .remote_interface import Remote


class YAE1K1Remote(Remote):
    """Remote interface for the YAE1K1 remote."""

    HVAC_MODE_COMMANDS = {
        HVACMode.COOL: YAE1K2Code.COOL_MODE,
        HVACMode.FAN_ONLY: YAE1K2Code.FAN_MODE,
    }
    FAN_MODE_COMMANDS = {
        FAN_LOW: YAE1K2Code.LOW,
        FAN_HIGH: YAE1K2Code.HIGH,
    }

    POWER_COMMAND = YAE1K2Code.POWER
    UP_COMMAND = YAE1K2Code.TEMP_UP
    DOWN_COMMAND = YAE1K2Code.TEMP_DOWN
