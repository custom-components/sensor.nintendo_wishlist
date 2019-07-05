import logging
import math
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity


__version__ = '1.0.0'
DOMAIN = 'nintendo_wishlist'
REQUIREMENTS = [
    'algoliasearch==2.0.0b5',
]

DEFAULT_NAME = 'Nintendo Wishlist Sensor'

SCAN_INTERVAL = timedelta(minutes=10)

CONF_WISHLIST = 'wishlist'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_WISHLIST): cv.ensure_list,
})

APP_ID = 'U3B6GR4UA3'
API_KEY = '9a20c93440cf63cf1a7008d75f7438bf'
QUERIES = [
    {
        'indexName': 'noa_aem_game_en_us',
        'params': 'query=&hitsPerPage=250&maxValuesPerFacet=30&page=0&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22generalFilters%3ADeals%22%5D%2C%5B%22platform%3ANintendo%20Switch%22%5D%5D'  # noqa
    },
    {
        'indexName': 'noa_aem_game_en_us',
        'params': 'query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=generalFilters&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%5D'  # noqa
    },
    {
        'indexName': 'noa_aem_game_en_us',
        'params': 'query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=platform&facetFilters=%5B%5B%22generalFilters%3ADeals%22%5D%5D'  # noqa
    }
]
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Setup the sensor platform."""
    sensors = [NintendoWishlistSensor(hass, config)]
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

    def __init__(self, hass, config):
        self._hass = hass
        self.attrs = {}
        self.wishlist = [g.lower() for g in config['wishlist']]
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Nintendo Wishlist'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return 'on sale'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return 'mdi:nintendo-switch'

    @property
    def device_state_attributes(self):
        return self.attrs

    async def async_update(self):
        """Get the latest data and updates the state."""
        from algoliasearch.search_client import SearchClient
        wish_list_matches = []
        async with SearchClient.create(APP_ID, API_KEY) as client:
            results = await client.multiple_queries_async(QUERIES)
            for game in results['results'][0]['hits']:
                if not game['title'].lower().startswith(tuple(self.wishlist)):
                    continue
                match = {
                    'box_art_url': (
                        'https://www.nintendo.com{}'.format(game['boxArt'])),
                    'normal_price': game['msrp'],
                    'percent_off': get_percent_off(
                        game['msrp'], game['salePrice']),
                    'sale_price': game['salePrice'],
                    'title': game['title'],
                }
                wish_list_matches.append(match)
        self.attrs['on_sale'] = wish_list_matches
        self._state = len(wish_list_matches)
