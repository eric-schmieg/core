"""Remote interface definitions for the Stateless AC Infrared integration."""

from abc import ABC
from typing import ClassVar

from infrared_protocols.commands import Command

from homeassistant.components.climate import HVACMode


class Remote(ABC):
    """Supported remote interfaces."""

    HVAC_MODES: ClassVar[dict[HVACMode, Command] | None] = None
    FAN_MODES: ClassVar[dict[str, Command] | None] = None
    SWING_MODES: ClassVar[dict[str, Command] | None] = None

    POWER_COMMAND: ClassVar[Command]
    UP_COMMAND: ClassVar[Command]
    DOWN_COMMAND: ClassVar[Command]
