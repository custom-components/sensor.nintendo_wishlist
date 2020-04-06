import enum
import logging
import math
from copy import copy
from datetime import timedelta
from typing import Any, Dict, List

import voluptuous as vol

from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .wishlist import Country, Wishlist

__version__ = "2.2.0"
DOMAIN = "nintendo_wishlist"

DEFAULT_NAME = "Nintendo Wishlist Sensor"

SCAN_INTERVAL = timedelta(minutes=10)

_LOGGER = logging.getLogger(__name__)


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
        self.fetcher = Wishlist(self.country, self.wishlist)

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
        games = await self.fetcher.fetch()
        games = self._parse_matches(games)
        self.attrs["on_sale"] = games
        self._State = len(games)

    def _parse_matches(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        for game in results:
            if not game["title"].lower().startswith(tuple(self.wishlist)):
                continue
            matches.append(game)
        return matches

    # async def _na_update(self):

    #    wish_list_matches = []
    #    queries = copy(QUERIES)
    #    params = queries[0]["params"]
    #    queries[0]["indexName"] = NA_INDEX_NAMES[self.country]
    #    async with SearchClient.create(APP_ID, API_KEY) as client:
    #        # Sets the default page to 0, if there are more pages we'll fetch those
    #        # after we know how many there are.
    #        query_params: str = params + "&page=0"
    #        queries[0]["params"] = query_params
    #        results = await client.multiple_queries_async(queries)
    #        wish_list_matches.extend(self._parse_matches(results["results"][0]["hits"]))
    #        # Check if there are more results than a single page.
    #        num_pages: int = results["results"][0]["nbPages"]
    #        if num_pages > 1:
    #            # Using pagination fetch the remaining results.
    #            for page_num in range(1, num_pages):
    #                # The page param is a 0-based index.  Since we already fetched page
    #                # 0, start at 1
    #                query_params: str = params + "&page=" + str(page_num)
    #                queries[0]["params"] = query_params
    #                results = await client.multiple_queries_async(queries)
    #                wish_list_matches.extend(
    #                    self._parse_matches(results["results"][0]["hits"])
    #                )
    #    self.attrs["on_sale"] = wish_list_matches
    #    self._state = len(wish_list_matches)

    # async def _eu_update(self):
    #    lang = COUNTRY_LANG[self.country]
    #    wish_list_matches = {}
    #    # NOTE: This endpoint requires the country to be lowercase.
    #    async with self.session.get(EU_SEARCH_URL.format(language=lang)) as resp:
    #        # The content-type is text/html so we need to specify None here.
    #        data = await resp.json(content_type=None)
    #        for game in data["response"]["docs"]:
    #            if not game["title"].lower().startswith(tuple(self.wishlist)):
    #                continue
    #            wish_list_matches[game["nsuid_txt"][0]] = {
    #                "box_art_url": "https:{}".format(game["image_url"]),
    #                "percent_off": game["price_discount_percentage_f"],
    #                "title": game["title"],
    #            }

    #            params = {
    #                "country": self.country,
    #                "ids": ",".join(wish_list_matches.keys()),
    #                "lang": "en",
    #            }
    #            async with self.session.get(EU_PRICE_URL, params=params) as r:
    #                prices = await r.json()
    #                for price in prices["prices"]:
    #                    n_id = str(price["title_id"])
    #                    wish_list_matches[n_id]["normal_price"] = price[
    #                        "regular_price"
    #                    ]["amount"]
    #                    wish_list_matches[n_id]["sale_price"] = price["discount_price"][
    #                        "amount"
    #                    ]
    #    self.attrs["on_sale"] = list(wish_list_matches.values())
    #    self._state = len(wish_list_matches)
