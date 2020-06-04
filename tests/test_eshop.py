"""Test the Eshop class."""
import pytest
from pytest_homeassistant.async_mock import AsyncMock, Mock

from custom_components.nintendo_wishlist.eshop import EShop, get_percent_off


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
    """Test a ValueError is raised if the games doesn't have a box art url."""
    wishlist = ["title1"]
    eshop = EShop("US", Mock(), wishlist)
    with pytest.raises(ValueError, match="Couldn't find box art"):
        game = {}
        eshop.get_na_switch_game(game)


def test_get_na_switch_game_bad_prefix_value_error():
    """Test a ValueError is raised if the game has the wrong extension."""
    wishlist = ["title1"]
    eshop = EShop("US", Mock(), wishlist)
    with pytest.raises(ValueError, match="Couldn't find box art"):
        game = {"boxArt": "https://nintendo.com/art.gif"}
        eshop.get_na_switch_game(game)


def test_get_na_switch_game_success():
    """Test we return the expected SwitchGame instance from the response."""
    wishlist = ["title1"]
    eshop = EShop("US", Mock(), wishlist)
    game = {
        "boxArt": "image.png",
        "msrp": 14.99,
        "nsuid": 70010000532,
        "salePrice": 8.24,
        "title": "Aggelos",
    }
    expected = {
        "box_art_url": "https://www.nintendo.comimage.png",
        "normal_price": "$14.99",
        "nsuid": 70010000532,
        "percent_off": 45,
        "sale_price": "$8.24",
        "title": "Aggelos",
    }
    assert expected == eshop.get_na_switch_game(game)


async def test__get_page():
    """Test _get_page returns the expected results."""
    wishlist = ["Aggelos"]
    eshop = EShop("US", Mock(), wishlist)
    client = Mock()
    games = [
        {
            "boxArt": "image.png",
            "msrp": 24.99,
            "nsuid": 70010000531,
            "salePrice": 9.99,
            "title": "Picross",
        },
        {
            "boxArt": "image.png",
            "msrp": 14.99,
            "nsuid": 70010000532,
            "salePrice": 8.24,
            "title": "Aggelos",
        },
    ]
    client.multiple_queries_async = AsyncMock(
        return_value={"results": [{"hits": games, "nbPages": 1}]}
    )
    actual = await eshop._get_page(client, [{"params": "f=1"}])

    expected = {
        "games": {
            70010000532: {
                "box_art_url": "https://www.nintendo.comimage.png",
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
