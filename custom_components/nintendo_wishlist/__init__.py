"""Nintendo Wishlist integration."""

from homeassistant import core
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_COUNTRY, DOMAIN
from .eshop import EShop
from .sensor_manager import NintendoWishlistDataUpdateCoordinator


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the platform.

    :returns: A boolean to indicate that initialization was successful.
    """
    eshop = EShop(config[CONF_COUNTRY].name, async_get_clientsession(hass))
    hass.data[DOMAIN]["coordinator"] = NintendoWishlistDataUpdateCoordinator(
        hass, eshop
    )
    hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    return True
