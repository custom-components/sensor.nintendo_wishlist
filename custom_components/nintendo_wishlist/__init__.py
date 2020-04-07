"""Nintendo Wishlist integration."""

from homeassistant import core
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_COUNTRY, DOMAIN
from .eshop import EShop
from .sensor_manager import NintendoWishlistDataUpdateCoordinator


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the platform.

    @NOTE: `config` is the full configuration dict, so to get values for this
    compomnent you must reference the domain key.

    :returns: A boolean to indicate that initialization was successful.
    """
    country = config[DOMAIN][CONF_COUNTRY].name
    eshop = EShop(country, async_get_clientsession(hass))
    hass.data[DOMAIN]["coordinator"] = NintendoWishlistDataUpdateCoordinator(
        hass, eshop
    )
    hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    return True
