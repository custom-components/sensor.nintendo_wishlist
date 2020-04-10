import copy
import enum
import logging
import math
from typing import Any, Dict, List, Tuple

import aiohttp
from algoliasearch.search_client import SearchClient

from .types import SwitchGame


_LOGGER = logging.getLogger(__name__)

# North American countries.
NA_COUNTRIES: Tuple[str] = ("CA", "US")
NA_INDEX_NAMES: Dict[str, str] = {
    "CA": "noa_aem_game_en_ca",
    "US": "noa_aem_game_en_us",
}

# Mapping of country code to language code.  NOTE: language must be lowercase
# in the URL to work.
COUNTRY_LANG: Dict[str, str] = {
    "AT": "at",
    "BE": "nl",
    "CA": "en",
    "CH": "de",
    "DE": "de",
    "ES": "es",
    "FR": "fr",
    "GB": "en",
    "IT": "it",
    "NL": "nl",
    "PT": "pt",
    "RU": "ru",
    "US": "en",
    "ZA": "za",
}


class Country(enum.Enum):
    """Enum for allowed countries."""

    AT = "Austria"
    BE = "Belgium"
    CA = "Canada"
    CH = "Schweiz/Suisse/Svizzera"
    DE = "Germany"
    ES = "Spain"
    FR = "France"
    GB = "UK/Ireland"
    IT = "Italy"
    NL = "Netherlands"
    PT = "Portugal"
    RU = "Russia"
    US = "United States"
    ZA = "South Africa"


# These are specific to European countries.
EU_SEARCH_URL = "https://searching.nintendo-europe.com/{language}/select?q=*&fq=type%3AGAME%20AND%20((playable_on_txt%3A%22HAC%22)%20AND%20(price_has_discount_b%3A%22true%22))%20AND%20sorting_title%3A*%20AND%20*%3A*&sort=price_discount_percentage_f%20desc%2C%20price_lowest_f%20desc&start=0&rows=500&wt=json&bf=linear(ms(priority%2CNOW%2FHOUR)%2C1.1e-11%2C0)"  # noqa
EU_PRICE_URL = "https://api.ec.nintendo.com/v1/price"

# Below constants used by North America (US and CA)
APP_ID = "U3B6GR4UA3"
API_KEY = "9a20c93440cf63cf1a7008d75f7438bf"
QUERIES = [
    {
        "indexName": "noa_aem_game_en_us",
        "params": "query=&hitsPerPage=350&maxValuesPerFacet=30&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22generalFilters%3ADeals%22%5D%2C%5B%22platform%3ANintendo%20Switch%22%5D%5D",  # noqa
    },
]


def get_percent_off(original_price: float, sale_price: float) -> int:
    """Returns the percentage off of the sale price vs original price.

    We round up and return an int.

    :param original_price: The original price.
    :param sale_price: The sale price.
    :returns: The percentage as an int.
    """
    return 100 - math.ceil(100 / (original_price / sale_price))


class EShop:
    """Encapsulates logic for retrieving eshop data for countries."""

    def __init__(
        self,
        country: Country,
        session: aiohttp.ClientSession,
        wishlist_terms: List[str],
    ):
        self.country = country
        self.session = session
        self.wishlist_terms = [term.lower() for term in wishlist_terms]
        self.fetch_method = self.fetch_na if country in NA_COUNTRIES else self.fetch_eu

    async def fetch_on_sale(self) -> Dict[int, SwitchGame]:
        """Fetch data about games that are on sale."""
        return await self.fetch_method()

    def get_na_switch_game(self, game: Dict[str, Any]) -> SwitchGame:
        """Get a SwitchGame from a json result."""
        box_art = game.get("boxArt", game.get("gallery"))
        if not box_art or not box_art.endswith((".png", ".jpg")):
            raise ValueError("Couldn't find box art: %s", game)

        return {
            "box_art_url": f"https://www.nintendo.com{box_art}",
            "normal_price": f"${game['msrp']}",
            "nsuid": int(game["nsuid"]),
            "percent_off": get_percent_off(game["msrp"], game["salePrice"]),
            "sale_price": f"${game['salePrice']}",
            "title": game["title"],
        }

    async def _get_page(
        self, client: SearchClient, queries: list, page_num: int
    ) -> Tuple[Dict[int, SwitchGame], int]:
        """Get all games for the provided page.

        :returns: A tuple where the first item is the dict of switch games and the 2nd
            is the total number of pages of results.
        """
        params = queries[0]["params"]
        query_params: str = f"{params}&page={page_num}"
        queries[0]["params"] = query_params
        results = await client.multiple_queries_async(queries)
        return (
            {
                int(r["nsuid"]): self.get_na_switch_game(r)
                for r in results["results"][0]["hits"]
                if r.get("boxArt")
            },
            results["results"][0]["nbPages"],
        )

    async def fetch_na(self) -> Dict[int, SwitchGame]:
        """Fetch data for North American countries."""
        games: Dict[int, SwitchGame] = {}
        queries = copy.copy(QUERIES)
        queries[0]["indexName"] = NA_INDEX_NAMES[self.country]
        async with SearchClient.create(APP_ID, API_KEY) as client:
            # Sets the default page to 0, if there are more pages we'll fetch those
            # after we know how many there are.
            games_on_sale, num_pages = await self._get_page(client, queries, page_num=0)
            games.update(games_on_sale)
            if num_pages > 1:
                for page_num in range(1, num_pages):
                    games_on_sale, _ = await self._get_page(client, queries, page_num)
                    games.update(games_on_sale)
        return games

    def get_eu_switch_game(self, game: dict) -> SwitchGame:
        try:
            return {
                "box_art_url": f"https:{game['image_url']}",
                "nsuid": int(game["nsuid_txt"][0]),
                "percent_off": game["price_discount_percentage_f"],
                "title": game["title"],
            }
        except Exception:
            _LOGGER.exception("Error getting eu game: %s", game)
            raise

    async def fetch_eu(self) -> Dict[int, SwitchGame]:
        lang = COUNTRY_LANG[self.country]
        games: Dict[int, SwitchGame] = {}
        # NOTE: This endpoint requires the country to be lowercase.
        async with self.session.get(EU_SEARCH_URL.format(language=lang)) as resp:
            # The content-type is text/html so we need to specify None here.
            data = await resp.json(content_type=None)
            games.update(self.parse_wishlist_matches(data["response"]["docs"]))

        # Add pricing data
        _LOGGER.warning("num matches: %s", len(games))
        pricing = await self.get_eu_pricing_data(list(games.keys()))
        for nsuid, item in pricing.items():
            games[nsuid].update(item)
        return games

    def parse_wishlist_matches(self, results: Dict[str, Any]) -> Dict[int, SwitchGame]:
        matches: Dict[int, SwitchGame] = {}
        for game in results:
            if not game["title"].lower().startswith(tuple(self.wishlist)):
                continue
            switch_game = self.get_eu_switch_game(game)
            matches[switch_game["nsuid"]] = switch_game
        return matches

    async def get_eu_pricing_data(self, nsuids: List[int]):
        pricing: Dict[int, Dict[str, Any]] = {}
        params = {
            "country": self.country,
            "ids": ",".join([str(nsuid) for nsuid in nsuids]),
            "lang": "en",
        }
        async with self.session.get(EU_PRICE_URL, params=params) as r:
            prices = await r.json()
            _LOGGER.warning("what are prices: %s", prices)
            for price in prices["prices"]:
                n_id = price["title_id"]
                pricing[n_id] = {
                    "normal_price": price["regular_price"]["amount"],
                    "sale_price": price["discount_price"]["amount"],
                }
        return pricing
