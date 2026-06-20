"""Button platform for the Stateless AC Infrared integration."""

from infrared_protocols.commands import Command

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .climate import StatelessClimate
from .const import CONF_REMOTE_TYPE, SUPPORTED_REMOTES
from .entity import IrEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Stateless AC Infrared calibrate button from config entry."""
    climate_entity: StatelessClimate = entry.runtime_data
    remote_type = entry.data[CONF_REMOTE_TYPE]
    remote_code_class = SUPPORTED_REMOTES[remote_type]
    async_add_entities([CalibrateButton(entry, climate_entity, remote_code_class)])


class CalibrateButton(IrEntity, ButtonEntity):
    """Button that triggers the AC calibration sequence."""

    _attr_translation_key = "calibrate"
    _attr_icon = "mdi:tune"

    def __init__(
        self,
        entry: ConfigEntry,
        climate_entity: StatelessClimate,
        remote_code_class: type[Command],
    ) -> None:
        """Initialize the calibrate button."""
        super().__init__(
            entry,
            climate_entity.infrared_entity_id,
            unique_id_suffix="calibrate",
            remote_code_class=remote_code_class,
        )
        self._climate_entity = climate_entity

    async def async_press(self) -> None:
        """Run the calibration sequence."""
        await self._climate_entity.async_calibrate()
