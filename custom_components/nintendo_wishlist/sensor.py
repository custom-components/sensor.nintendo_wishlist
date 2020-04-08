import logging

from homeassistant import core

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: core.HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    _LOGGER.warning("setting up sensor")
    await hass.data[DOMAIN]["sensor_manager"].async_register_component(
        "sensor", async_add_entities
    )
