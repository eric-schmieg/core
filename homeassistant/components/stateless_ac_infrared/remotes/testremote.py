"""Test remote definitions for the Stateless AC Infrared integration."""

from infrared_protocols.codes.general_electric.yae1k2 import YAE1K2Code

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
    FAN_TOP,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_ON,
    SWING_VERTICAL,
    HVACMode,
)

from .remote_interface import Remote


class TestRemote(Remote):
    """Remote interface for the Test remote."""

    HVAC_MODES = {
        HVACMode.COOL: YAE1K2Code.COOL_MODE,
        HVACMode.FAN_ONLY: YAE1K2Code.FAN_MODE,
        HVACMode.HEAT: YAE1K2Code.COOL_MODE,
        HVACMode.DRY: YAE1K2Code.COOL_MODE,
        HVACMode.AUTO: YAE1K2Code.COOL_MODE,
    }

    FAN_MODES = {
        FAN_ON: YAE1K2Code.LOW,
        FAN_OFF: YAE1K2Code.LOW,
        FAN_AUTO: YAE1K2Code.LOW,
        FAN_LOW: YAE1K2Code.LOW,
        FAN_MEDIUM: YAE1K2Code.LOW,
        FAN_HIGH: YAE1K2Code.LOW,
        FAN_TOP: YAE1K2Code.LOW,
        FAN_MIDDLE: YAE1K2Code.LOW,
        FAN_FOCUS: YAE1K2Code.LOW,
        FAN_DIFFUSE: YAE1K2Code.LOW,
    }

    SWING_MODES = {
        SWING_ON: YAE1K2Code.LOW,
        SWING_OFF: YAE1K2Code.LOW,
        SWING_BOTH: YAE1K2Code.LOW,
        SWING_VERTICAL: YAE1K2Code.LOW,
        SWING_HORIZONTAL: YAE1K2Code.LOW,
    }

    POWER_COMMAND = YAE1K2Code.POWER
    UP_COMMAND = YAE1K2Code.TEMP_UP
    DOWN_COMMAND = YAE1K2Code.TEMP_DOWN
