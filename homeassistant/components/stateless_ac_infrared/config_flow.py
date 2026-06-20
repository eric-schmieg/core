"""Config flow for the Stateless AC Infrared integration."""

from typing import Any

import voluptuous as vol

from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
    async_get_emitters,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_TEMPERATURE_UNIT, UnitOfTemperature
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_REMOTE_TYPE,
    CONF_TEMP_SENSOR,
    CONF_TEMP_STEP,
    DEFAULT_MAX_TEMP,
    DEFAULT_MAX_TEMP_C,
    DEFAULT_MIN_TEMP,
    DEFAULT_MIN_TEMP_C,
    DEFAULT_TEMP_STEP,
    DEFAULT_TEMPERATURE_UNIT,
    DOMAIN,
    SUPPORTED_REMOTES,
)


class StatelessAcInfraredConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stateless AC Infrared."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._config_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        emitter_entity_ids = async_get_emitters(self.hass)
        if not emitter_entity_ids:
            return self.async_abort(reason="no_emitters")

        if user_input is not None:
            entity_id = user_input[CONF_INFRARED_ENTITY_ID]
            await self.async_set_unique_id(
                f"stateless_ac_infrared_{user_input[CONF_REMOTE_TYPE]}_{entity_id}"
            )
            self._abort_if_unique_id_configured()

            self._config_data = user_input
            return await self.async_step_temperature_limits()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REMOTE_TYPE): SelectSelector(
                        SelectSelectorConfig(
                            options=list(SUPPORTED_REMOTES.keys()),
                            translation_key=CONF_REMOTE_TYPE,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_INFRARED_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain=INFRARED_DOMAIN,
                            include_entities=emitter_entity_ids,
                        )
                    ),
                    vol.Optional(CONF_TEMP_SENSOR): EntitySelector(
                        EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Required(
                        CONF_TEMPERATURE_UNIT, default=DEFAULT_TEMPERATURE_UNIT
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(
                                    value=UnitOfTemperature.FAHRENHEIT,
                                    label="Fahrenheit",
                                ),
                                SelectOptionDict(
                                    value=UnitOfTemperature.CELSIUS,
                                    label="Celsius",
                                ),
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_temperature_limits(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure the allowed temperature range."""
        errors: dict[str, str] = {}

        unit = UnitOfTemperature(self._config_data[CONF_TEMPERATURE_UNIT])
        default_min_temp = (
            DEFAULT_MIN_TEMP_C
            if unit == UnitOfTemperature.CELSIUS
            else DEFAULT_MIN_TEMP
        )
        default_max_temp = (
            DEFAULT_MAX_TEMP_C
            if unit == UnitOfTemperature.CELSIUS
            else DEFAULT_MAX_TEMP
        )

        if user_input is not None:
            if user_input[CONF_MIN_TEMP] >= user_input[CONF_MAX_TEMP]:
                errors["base"] = "invalid_temp_range"
            else:
                config_data = {**self._config_data, **user_input}
                title = "Air Conditioner"

                return self.async_create_entry(title=title, data=config_data)

        return self.async_show_form(
            step_id="temperature_limits",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MIN_TEMP, default=default_min_temp
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=1,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement=unit,
                        )
                    ),
                    vol.Required(
                        CONF_MAX_TEMP, default=default_max_temp
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=1,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement=unit,
                        )
                    ),
                    vol.Required(
                        CONF_TEMP_STEP, default=DEFAULT_TEMP_STEP
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=["1", "0.5", "0.1"],
                            translation_key=CONF_TEMP_STEP,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )
