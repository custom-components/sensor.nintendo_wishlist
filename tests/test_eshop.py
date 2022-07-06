"""Test the Eshop class."""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.nintendo_wishlist.eshop import (
    EU_PRICE_URL,
    EU_SEARCH_URL,
    NO_BOX_ART_URL,
    EShop,
    get_percent_off,
)


@pytest.fixture
def client_mock():
    """Pytest fixture to mock the algoliasearch client."""
    client = Mock()
    games = [
        {
            "boxart": "https://assets.nintendo.com/0/box-eShop",
            "msrp": 24.99,
            "nsuid": 70010000531,
            "salePrice": 9.99,
            "title": "Picross",
        },
        {
            "boxart": "https://assets.nintendo.com/1/box-eShop",
            "msrp": 14.99,
            "nsuid": 70010000532,
            "salePrice": 8.24,
            "title": "Aggelos",
        },
    ]
    client.multiple_queries_async = AsyncMock(
        return_value={"results": [{"hits": games, "nbPages": 1}]}
    )
    return client


def test_get_percent_off():
    """Test get_percent_off returns correct value."""
    original_price = 14.99
    sale_price = 8.24
    assert 45 == get_percent_off(original_price, sale_price)


def test_init_sets_correct_fetch_method():
    """Test fetch_method is set correctly based on country."""
    wishlist = ["title1"]
    eshop = EShop("US", Mock(), wishlist)
    assert eshop.fetch_na == eshop.fetch_method

    eshop = EShop("DE", Mock(), wishlist)
    assert eshop.fetch_eu == eshop.fetch_method


def test_get_na_switch_game_no_box_art_value_error():
    """Test we use no box art url if the games doesn't have a box art url."""
    wishlist = ["title1"]
    eshop = EShop("US", Mock(), wishlist)
    game = {
        "msrp": 14.99,
        "nsuid": 70010000532,
        "salePrice": 8.24,
        "title": "Aggelos",
    }
    expected = {
        "box_art_url": NO_BOX_ART_URL,
        "normal_price": "$14.99",
        "nsuid": 70010000532,
        "percent_off": 45,
        "sale_price": "$8.24",
        "title": "Aggelos",
    }
    assert expected == eshop.get_na_switch_game(game)


def test_get_na_switch_game_success():
    """Test we return the expected SwitchGame instance from the response."""
    wishlist = ["title1"]
    eshop = EShop("US", Mock(), wishlist)
    game = {
        "boxart": "image.png",
        "msrp": 14.99,
        "nsuid": 70010000532,
        "salePrice": 8.24,
        "title": "Aggelos",
    }
    expected = {
        "box_art_url": "image.png",
        "normal_price": "$14.99",
        "nsuid": 70010000532,
        "percent_off": 45,
        "sale_price": "$8.24",
        "title": "Aggelos",
    }
    assert expected == eshop.get_na_switch_game(game)


async def test__get_page(client_mock):
    """Test _get_page returns the expected results."""
    wishlist = ["Aggelos"]
    eshop = EShop("US", Mock(), wishlist)
    actual = await eshop._get_page(client_mock, [{"params": "f=1"}])

    expected = {
        "games": {
            70010000532: {
                "box_art_url": "https://assets.nintendo.com/1/box-eShop",
                "normal_price": "$14.99",
                "nsuid": 70010000532,
                "percent_off": 45,
                "sale_price": "$8.24",
                "title": "Aggelos",
            }
        },
        "num_pages": 1,
    }
    assert expected == actual


async def test_fetch_na(client_mock):
    """Test the fetch_na method returns the expected results."""
    wishlist = ["Aggelos"]
    eshop = EShop("US", Mock(), wishlist)
    with patch(
        "custom_components.nintendo_wishlist.eshop.SearchClient.create"
    ) as create:
        create.return_value.__aenter__.return_value = client_mock
        actual = await eshop.fetch_na()

        expected = {
            70010000532: {
                "box_art_url": "https://assets.nintendo.com/1/box-eShop",
                "normal_price": "$14.99",
                "nsuid": 70010000532,
                "percent_off": 45,
                "sale_price": "$8.24",
                "title": "Aggelos",
            }
        }
        assert expected == actual


async def test__get_eu_page(hass):
    """Test the _get_eu_page method returns the expected result."""
    response = {
        "response": {
            "numFound": 2,
            "docs": [
                {
                    "title": "Aggelos",
                    "image_url": "//nintendo.com/image.png",
                    "nsuid_txt": ["70010000532"],
                    "price_discount_percentage_f": 10,
                },
                {
                    "title": "Resident Evil",
                    "image_url": "//nintendo.com/image.png",
                    "nsuid_txt": ["70010000531"],
                    "price_discount_percentage_f": 60,
                },
            ],
        }
    }

    mocker = AiohttpClientMocker()
    mocker.get(EU_SEARCH_URL.format(start=0, language="de"), json=response)
    wishlist = ["Aggelos"]
    async with mocker.create_session(hass.loop) as session:
        eshop = EShop("DE", session, wishlist)
        actual = await eshop._get_eu_page()
        expected = {
            "games": {
                70010000532: {
                    "box_art_url": "https://nintendo.com/image.png",
                    "nsuid": 70010000532,
                    "percent_off": 10,
                    "title": "Aggelos",
                }
            },
            "num_pages": 1,
        }
        assert expected == actual


def test_get_eu_switch_game():
    """Test the get_eu_switch_game method returns the expected result."""
    wishlist = ["Aggelos"]
    eshop = EShop("DE", Mock(), wishlist)
    game = {
        "title": "Aggelos",
        "image_url": "//nintendo.com/image.png",
        "nsuid_txt": ["70010000532"],
        "price_discount_percentage_f": 10,
    }
    actual = eshop.get_eu_switch_game(game)
    expected = {
        "box_art_url": "https://nintendo.com/image.png",
        "nsuid": 70010000532,
        "percent_off": 10,
        "title": "Aggelos",
    }
    assert expected == actual


def test_get_eu_switch_game_with_https_prefix_on_image_url():
    """Regression test for when the image_url actually has a protocol."""
    wishlist = ["Aggelos"]
    eshop = EShop("DE", Mock(), wishlist)
    game = {
        "title": "Aggelos",
        "image_url": "https://nintendo.com/image.png",
        "nsuid_txt": ["70010000532"],
        "price_discount_percentage_f": 10,
    }
    actual = eshop.get_eu_switch_game(game)
    expected = {
        "box_art_url": "https://nintendo.com/image.png",
        "nsuid": 70010000532,
        "percent_off": 10,
        "title": "Aggelos",
    }
    assert expected == actual


async def test_fetch_eu(hass):
    """Test the fetch_eu method returns the expected result."""
    page_response = {
        "games": {
            70010000532: {
                "box_art_url": "https://nintendo.com/image.png",
                "nsuid": 70010000532,
                "percent_off": 10,
                "title": "Aggelos",
            }
        },
        "num_pages": 1,
    }
    pricing_response = {
        "prices": [
            {
                "title_id": 70010000532,
                "regular_price": {"amount": 24.99},
                "discount_price": {"amount": 8.24},
            }
        ]
    }

    wishlist = ["Aggelos"]
    mocker = AiohttpClientMocker()
    mocker.get(EU_PRICE_URL, json=pricing_response)
    async with mocker.create_session(hass.loop) as session:
        eshop = EShop("DE", session, wishlist)
        eshop._get_eu_page = AsyncMock(return_value=page_response)
        actual = await eshop.fetch_eu()
        expected = {
            70010000532: {
                "box_art_url": "https://nintendo.com/image.png",
                "nsuid": 70010000532,
                "percent_off": 10,
                "title": "Aggelos",
                "normal_price": 24.99,
                "sale_price": 8.24,
            }
        }
        assert expected == actual


async def test_get_eu_pricing_data_missing_discount_price(
    hass,
) -> None:
    """Test we don't raise an exception if the discount price is missing."""
    pricing_response = {
        "prices": [
            {
                "title_id": 70010000532,
                "regular_price": {"amount": 24.99},
            }
        ]
    }
    wishlist = ["Aggelos"]
    mocker = AiohttpClientMocker()
    mocker.get(EU_PRICE_URL, json=pricing_response)
    async with mocker.create_session(hass.loop) as session:
        eshop = EShop("DE", session, wishlist)
        nsuids = [70010000532]
        actual = await eshop.get_eu_pricing_data(nsuids)
        expected = {70010000532: {"normal_price": 24.99, "sale_price": "?"}}
        assert expected == actual
