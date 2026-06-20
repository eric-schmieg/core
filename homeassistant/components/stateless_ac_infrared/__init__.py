"""The General Electric Stateless Air Conditioners integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_INFRARED_ENTITY_ID
from .services import async_setup_services

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.CLIMATE]

CONFIG_SCHEMA = cv.config_entry_only_config_schema("stateless_ac_infrared")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Stateless AC Infrared integration."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up General Electric Stateless AC from a config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    if hass.states.get(infrared_entity_id) is None:
        raise ConfigEntryNotReady(
            f"Infrared entity {infrared_entity_id} is not yet available"
        )
    entry.runtime_data = None
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.CLIMATE])
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.BUTTON])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
