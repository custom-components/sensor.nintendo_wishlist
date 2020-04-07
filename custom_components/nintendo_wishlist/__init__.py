"""Nintendo Wishlist integration."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant import core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_COUNTRY, CONF_WISHLIST, DOMAIN
from .eshop import Country, EShop
from .sensor_manager import NintendoWishlistDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_WISHLIST): cv.ensure_list,
        vol.Required(CONF_COUNTRY): cv.enum(Country),
    }
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the platform.

    @NOTE: `config` is the full configuration dict, so to get values for this
    compomnent you must reference the domain key.

    :returns: A boolean to indicate that initialization was successful.
    """
    _LOGGER.warning("async_setup conf: %s", config)
    country = config[CONF_COUNTRY]
    eshop = EShop(country, async_get_clientsession(hass))
    hass.data[DOMAIN] = {
        "coordinator": NintendoWishlistDataUpdateCoordinator(hass, eshop)
    }
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    )
    return True
