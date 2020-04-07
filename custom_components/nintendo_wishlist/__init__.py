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
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_WISHLIST): cv.ensure_list,
                vol.Required(CONF_COUNTRY): cv.enum(Country),
            }
        )
    },
    # The full HA configurations gets passed to `async_setup` so we need to allow
    # extra keys.
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the platform.

    @NOTE: `config` is the full dict from `configuration.yaml`.

    :returns: A boolean to indicate that initialization was successful.
    """
    conf = config[DOMAIN]
    _LOGGER.warning("async_setup conf: %s", conf)
    country = conf[CONF_COUNTRY]
    eshop = EShop(country, async_get_clientsession(hass))
    hass.data[DOMAIN] = {
        "conf": conf,
        "coordinator": NintendoWishlistDataUpdateCoordinator(hass, eshop),
    }
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(hass, "sensor", DOMAIN, {}, conf)
    )
    return True
