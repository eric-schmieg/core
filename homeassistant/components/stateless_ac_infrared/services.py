"""Services for the Stateless AC Infrared integration."""

import voluptuous as vol

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import service

from .const import ATTR_TARGET_TEMPERATURE, DOMAIN, SERVICE_CALIBRATE


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Stateless AC Infrared integration."""
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_CALIBRATE,
        entity_domain=CLIMATE_DOMAIN,
        schema={vol.Optional(ATTR_TARGET_TEMPERATURE): vol.Coerce(float)},
        func="async_calibrate",
    )
