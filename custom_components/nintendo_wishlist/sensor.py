import enum
import logging
import math
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity


__version__ = '2.0.1'
DOMAIN = 'nintendo_wishlist'
REQUIREMENTS = [
    'algoliasearch==2.0.0b5',
]

DEFAULT_NAME = 'Nintendo Wishlist Sensor'

SCAN_INTERVAL = timedelta(minutes=10)

# North American countries.
NA_COUNTRIES = ('CA', 'US')
NA_INDEX_NAMES = {
    'CA': 'noa_aem_game_en_ca',
    'US': 'noa_aem_game_en_us',
}

# Mapping of country code to language code.  NOTE: language must be lowercase
# in the URL to work.
COUNTRY_LANG = {
    'AT': 'at',
    'BE': 'nl',
    'CA': 'en',
    'CH': 'de',
    'DE': 'de',
    'ES': 'es',
    'FR': 'fr',
    'GB': 'en',
    'IT': 'it',
    'NL': 'nl',
    'PT': 'pt',
    'RU': 'ru',
    'US': 'en',
    'ZA': 'za',
}


class Country(enum.Enum):
    """Enum for allowed countries."""

    AT = 'Austria'
    BE = 'Belgium'
    CA = 'Canada'
    CH = 'Schweiz/Suisse/Svizzera'
    DE = 'Germany'
    ES = 'Spain'
    FR = 'France'
    GB = 'UK/Ireland'
    IT = 'Italy'
    NL = 'Netherlands'
    PT = 'Portugal'
    RU = 'Russia'
    US = 'United States'
    ZA = 'South Africa'


CONF_COUNTRY = 'country'
CONF_WISHLIST = 'wishlist'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_WISHLIST): cv.ensure_list,
    vol.Required(CONF_COUNTRY): cv.enum(Country),
})

# These are specific to European countries.
EU_SEARCH_URL = 'https://searching.nintendo-europe.com/{language}/select?q=*&fq=type%3AGAME%20AND%20((playable_on_txt%3A%22HAC%22)%20AND%20(price_has_discount_b%3A%22true%22))%20AND%20sorting_title%3A*%20AND%20*%3A*&sort=price_discount_percentage_f%20desc%2C%20price_lowest_f%20desc&start=0&rows=500&wt=json&bf=linear(ms(priority%2CNOW%2FHOUR)%2C1.1e-11%2C0)'  # noqa
EU_PRICE_URL = 'https://api.ec.nintendo.com/v1/price'

# Below constants used by North America (US and CA)
APP_ID = 'U3B6GR4UA3'
API_KEY = '9a20c93440cf63cf1a7008d75f7438bf'
QUERIES = [
    {
        'indexName': 'noa_aem_game_en_us',
        'params': 'query=&hitsPerPage=350&maxValuesPerFacet=30&page=0&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22generalFilters%3ADeals%22%5D%2C%5B%22platform%3ANintendo%20Switch%22%5D%5D'  # noqa
    },
]
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Setup the sensor platform."""
    sensors = [NintendoWishlistSensor(config)]
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

    def __init__(self, config):
        import aiohttp
        self.attrs = {}
        self.country = config['country'].name
        self.wishlist = [g.lower() for g in config['wishlist']]
        self.session = aiohttp.ClientSession()
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
        if self.country in NA_COUNTRIES:
            await self._na_update()
        else:
            await self._eu_update()

    async def _na_update(self):
        from algoliasearch.search_client import SearchClient
        wish_list_matches = []
        QUERIES[0]['indexName'] = NA_INDEX_NAMES[self.country]
        async with SearchClient.create(APP_ID, API_KEY) as client:
            results = await client.multiple_queries_async(QUERIES)
            for game in results['results'][0]['hits']:
                if not game['title'].lower().startswith(tuple(self.wishlist)):
                    continue
                match = {
                    'box_art_url': (
                        'https://www.nintendo.com{}'.format(game['boxArt'])),
                    'normal_price': '${}'.format(game['msrp']),
                    'percent_off': get_percent_off(
                        game['msrp'], game['salePrice']),
                    'sale_price': '${}'.format(game['salePrice']),
                    'title': game['title'],
                }
                wish_list_matches.append(match)
        self.attrs['on_sale'] = wish_list_matches
        self._state = len(wish_list_matches)

    async def _eu_update(self):
        lang = COUNTRY_LANG[self.country]
        wish_list_matches = {}
        # NOTE: This endpoint requires the country to be lowercase.
        async with self.session.get(
                EU_SEARCH_URL.format(language=lang)) as resp:
            # The content-type is text/html so we need to specify None here.
            data = await resp.json(content_type=None)
            for game in data['response']['docs']:
                if not game['title'].lower().startswith(tuple(self.wishlist)):
                    continue
                wish_list_matches[game['nsuid_txt'][0]] = {
                    'box_art_url': 'https:{}'.format(game['image_url']),
                    'percent_off': game['price_discount_percentage_f'],
                    'title': game['title'],
                }

                params = {
                    'country': self.country,
                    'ids': ','.join(wish_list_matches.keys()),
                    'lang': 'en',
                }
                async with self.session.get(EU_PRICE_URL, params=params) as r:
                    prices = await r.json()
                    for price in prices['prices']:
                        n_id = str(price['title_id'])
                        wish_list_matches[n_id]['normal_price'] = (
                            price['regular_price']['amount'])
                        wish_list_matches[n_id]['sale_price'] = (
                            price['discount_price']['amount'])
        self.attrs['on_sale'] = list(wish_list_matches.values())
        self._state = len(wish_list_matches)
