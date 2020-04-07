import logging
import math
from typing import Any, Dict, List

import voluptuous as vol

from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .const import DOMAIN
from .eshop import Country, EShop, NA_COUNTRIES


_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Nintendo Wishlist Sensor"

CONF_COUNTRY = "country"
CONF_WISHLIST = "wishlist"
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_WISHLIST): cv.ensure_list,
        vol.Required(CONF_COUNTRY): cv.enum(Country),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    _LOGGER.warning("setup config? %s", config)
    _LOGGER.warning("setup coordinator? %s", hass.data[DOMAIN])
    sensors = [
        NintendoWishlistSensor(hass, config, game) for game in config["wishlist"]
    ]
    sensors.append(NintendoWishlistSensor(hass, config))
    async_add_entities(sensors, True)


def get_percent_off(original_price: float, sale_price: float) -> int:
    """Returns the percentage off of the sale price vs original price.

    We round up and return an int.

    :param original_price: The original price.
    :param sale_price: The sale price.
    :returns: The percentage as an int.
    """
    return 100 - math.ceil(100 / (original_price / sale_price))


class NintendoWishlistSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass, config, game: str = None):
        self.attrs = {}
        self.country = config["country"].name
        self.wishlist = [g.lower() for g in config["wishlist"]]
        self.session = async_get_clientsession(hass)
        self.game = None
        # This attribute holds the title before we lowercase it.
        self._game = None
        if game is not None:
            self._game = game
            self.game = game.lower()
            self.wishlist = [self.game]
        self._state = None
        self.eshop = EShop(self.country, self.session)

    @property
    def entity_id(self):
        """Return the entity id of the sensor."""
        if self.game:
            return "sensor.nintendo_wishlist_{}".format(slugify(self.game))
        return "sensor.nintendo_wishlist"

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._game:
            return self._game
        return "Nintendo Wishlist"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return "mdi:nintendo-switch"

    @property
    def device_state_attributes(self):
        return self.attrs

    async def async_update(self):
        """Get the latest data and updates the state."""
        games = await self.eshop.fetch_on_sale()
        games = self._parse_matches(games)
        if self.country not in NA_COUNTRIES:
            # We need to look up the pricing in a separate api call.
            nsuids = [game["nsuid"] for game in games]
            pricing = await self.eshop.get_eu_pricing_data(nsuids)
            for game in games:
                game["normal_price"] = pricing[game["nsuid"]]["normal_price"]
                game["sale_price"] = pricing[game["nsuid"]]["sale_price"]
        self.attrs["on_sale"] = games
        self._state = len(games)

    def _parse_matches(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        for game in results:
            if not game["title"].lower().startswith(tuple(self.wishlist)):
                continue
            matches.append(game)
        return matches
