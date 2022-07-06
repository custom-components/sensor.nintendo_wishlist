import copy
import enum
import logging
import math
from typing import Any, Dict, List, Tuple

import aiohttp
from algoliasearch.search_client import SearchClient

from .types import EShopResults, ResultsDict, SwitchGame

_LOGGER = logging.getLogger(__name__)

# North American countries.
NA_COUNTRIES: tuple[str] = ("CA", "US")
NA_INDEX_NAMES: dict[str, str] = {
    "CA": "ncom_game_en_ca",
    "US": "ncom_game_en_us",
}

# Mapping of country code to language code.  NOTE: language must be lowercase
# in the URL to work.
COUNTRY_LANG: dict[str, str] = {
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
# NOTE: This endpoint requires the language to be lowercase.
EU_SEARCH_URL = "https://searching.nintendo-europe.com/{language}/select?q=*&fq=type%3AGAME%20AND%20((playable_on_txt%3A%22HAC%22)%20AND%20(price_has_discount_b%3A%22true%22))%20AND%20sorting_title%3A*%20AND%20*%3A*&sort=price_discount_percentage_f%20desc%2C%20price_lowest_f%20desc&start={start}&rows=500&wt=json&bf=linear(ms(priority%2CNOW%2FHOUR)%2C1.1e-11%2C0)"  # noqa
EU_PRICE_URL = "https://api.ec.nintendo.com/v1/price"

# Below constants used by North America (US and CA)
APP_ID = "U3B6GR4UA3"
API_KEY = "c4da8be7fd29f0f5bfa42920b0a99dc7"
QUERIES = [
    {
        "indexName": "ncom_game_en_us",
        "params": "query=&hitsPerPage=350&maxValuesPerFacet=30&page=0&analytics=false&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22genres%22%2C%22howToShop%22%2C%22virtualConsole%22%2C%22franchises%22%2C%22priceRange%22%2C%22esrbRating%22%2C%22playerFilters%22%5D&tagFilters=&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%2C%5B%22generalFilters%3ADeals%22%5D%5D",  # noqa
    },
]

NO_BOX_ART_URL = "https://raw.githubusercontent.com/custom-components/sensor.nintendo_wishlist/master/assets/no-box-art.png"  # noqa


def get_percent_off(original_price: float, sale_price: float) -> int:
    """Returns the percentage off of the sale price vs original price.

    We round up and return an int.

    :param original_price: The original price.
    :param sale_price: The sale price.
    :returns: The percentage as an int.
    """
    return 100 - math.ceil(100 / (original_price / sale_price))


class EShop:
    """Encapsulates logic for retrieving eshop sale data for countries."""

    def __init__(
        self,
        country: Country,
        session: aiohttp.ClientSession,
        wishlist_terms: list[str],
    ):
        self.country = country
        self.session = session
        self.wishlist_terms = [term.lower() for term in wishlist_terms]
        self.fetch_method = self.fetch_na if country in NA_COUNTRIES else self.fetch_eu

    async def fetch_on_sale(self) -> EShopResults:
        """Fetch data about games that are on sale."""
        return await self.fetch_method()

    def get_na_switch_game(self, game: dict[str, Any]) -> SwitchGame:
        """Get a SwitchGame from a json result."""
        box_art = game.get("boxart", game.get("gallery"))
        if not box_art:
            box_art_url = NO_BOX_ART_URL
        else:
            box_art_url = box_art

        return {
            "box_art_url": box_art_url,
            "normal_price": f"${game['msrp']}",
            "nsuid": int(game["nsuid"]),
            "percent_off": get_percent_off(game["msrp"], game["salePrice"]),
            "sale_price": f"${game['salePrice']}",
            "title": game["title"],
        }

    async def _get_page(
        self, client: SearchClient, queries: list, page_num: int = 0
    ) -> ResultsDict:
        """Get all games for the provided page.

        :returns: A tuple where the first item is the dict of switch games and the 2nd
            is the total number of pages of results.
        """
        game_results: dict[int, SwitchGame] = {}
        result: ResultsDict = {"games": game_results, "num_pages": 1}
        params = queries[0]["params"]
        query_params: str = f"{params}&page={page_num}"
        queries[0]["params"] = query_params
        data = await client.multiple_queries_async(queries)
        games = [r for r in data["results"][0]["hits"]]
        result["games"] = self.filter_wishlist_matches(games)
        result["num_pages"] = data["results"][0]["nbPages"]
        return result

    async def fetch_na(self) -> dict[int, SwitchGame]:
        """Fetch data for North American countries."""
        games: dict[int, SwitchGame] = {}
        queries = copy.copy(QUERIES)
        queries[0]["indexName"] = NA_INDEX_NAMES[self.country]
        async with SearchClient.create(APP_ID, API_KEY) as client:
            # Sets the default page to 0, if there are more pages we'll fetch those
            # after we know how many there are.
            results = await self._get_page(client, queries)
            games.update(results["games"])
            if results["num_pages"] > 1:
                for page_num in range(1, results["num_pages"]):
                    results = await self._get_page(client, queries, page_num)
                    games.update(results["games"])
        return games

    async def _get_eu_page(self, page: int = 0) -> ResultsDict:
        """Get all games on sale for the provided page."""
        games: dict[int, SwitchGame] = {}
        result: ResultsDict = {"games": games, "num_pages": 1}

        # 1st page starts at 0, 2nd page starts at 500, etc.
        start = page * 500
        lang = COUNTRY_LANG[self.country]
        url = EU_SEARCH_URL.format(start=start, language=lang)
        async with self.session.get(url) as resp:
            # The content-type is text/html so we need to specify None here.
            data = await resp.json(content_type=None)
            result["num_pages"] = math.ceil(data["response"]["numFound"] / 500)
            result["games"].update(
                self.filter_wishlist_matches(data["response"]["docs"])
            )

        return result

    def get_eu_switch_game(self, game: dict) -> SwitchGame:
        try:
            image_url = game["image_url"]
            if not image_url.startswith("https:"):
                image_url = f"https:{image_url}"
            return {
                "box_art_url": image_url,
                "nsuid": int(game["nsuid_txt"][0]),
                "percent_off": game["price_discount_percentage_f"],
                "title": game["title"],
            }
        except Exception:
            _LOGGER.exception("Error getting eu game: %s", game)
            raise

    async def fetch_eu(self) -> dict[int, SwitchGame]:
        games: dict[int, SwitchGame] = {}

        results = await self._get_eu_page()
        games.update(results["games"])
        if results["num_pages"] > 1:
            for page_num in range(1, results["num_pages"]):
                results = await self._get_eu_page(page_num)
                games.update(results["games"])

        # Add pricing data
        pricing = await self.get_eu_pricing_data(list(games.keys()))
        for nsuid, item in pricing.items():
            games[nsuid].update(item)
        return games

    def filter_wishlist_matches(
        self, results: list[dict[str, Any]]
    ) -> dict[int, SwitchGame]:
        """Filter wishlist matches from a list of games on sale."""
        matches: dict[int, SwitchGame] = {}
        for game in results:
            if not game["title"].lower().startswith(tuple(self.wishlist_terms)):
                continue
            if self.country in NA_COUNTRIES:
                switch_game = self.get_na_switch_game(game)
            else:
                switch_game = self.get_eu_switch_game(game)
            matches[switch_game["nsuid"]] = switch_game
        return matches

    async def get_eu_pricing_data(self, nsuids: list[int]):
        """Get EU pricing data for a list of nsuids."""
        pricing: dict[int, dict[str, Any]] = {}
        params = {
            "country": self.country,
            "ids": ",".join([str(nsuid) for nsuid in nsuids]),
            "lang": "en",
        }
        async with self.session.get(EU_PRICE_URL, params=params) as r:
            prices = await r.json()
            for price in prices["prices"]:
                n_id = price["title_id"]
                pricing[n_id] = {
                    "normal_price": price["regular_price"]["amount"],
                    "sale_price": price.get("discount_price", {}).get("amount", "?"),
                }
        return pricing
