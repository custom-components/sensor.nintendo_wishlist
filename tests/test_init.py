"""Test the setup of the component."""
from datetime import timedelta

from custom_components.nintendo_wishlist.const import DEFAULT_SCAN_INTERVAL, DOMAIN
from custom_components.nintendo_wishlist.eshop import Country
from pytest_homeassistant.async_mock import AsyncMock, Mock, patch

from homeassistant.setup import async_setup_component


async def test_async_setup_basic_success(hass):
    """Test async_setup succeeds in the most basic case."""
    config = {"nintendo_wishlist": {"country": "US", "wishlist": ["title1", "title2"]}}
    # Mocking to avoid network calls in test.
    with patch("custom_components.nintendo_wishlist.EShop") as mock_eshop:
        mock_instance = Mock()
        mock_instance.fetch_on_sale.return_value = AsyncMock()
        mock_eshop.return_value = mock_instance
        assert await async_setup_component(hass, DOMAIN, config) is True

    expected = {
        "country": Country.US,
        "scan_interval": DEFAULT_SCAN_INTERVAL,
        "wishlist": ["title1", "title2"],
    }
    assert expected == hass.data[DOMAIN]["conf"]
    assert DEFAULT_SCAN_INTERVAL == hass.data[DOMAIN]["coordinator"].update_interval


async def test_async_setup_custom_scan_interval(hass):
    """Test async_setup with a custom scan_interval."""
    scan_interval = timedelta(days=1)
    config = {
        "nintendo_wishlist": {
            "country": "US",
            "scan_interval": scan_interval,
            "wishlist": ["title1", "title2"],
        }
    }
    # Mocking to avoid network calls in test.
    with patch("custom_components.nintendo_wishlist.EShop") as mock_eshop:
        mock_instance = Mock()
        mock_instance.fetch_on_sale.return_value = AsyncMock()
        mock_eshop.return_value = mock_instance
        assert await async_setup_component(hass, DOMAIN, config) is True

    expected = {
        "country": Country.US,
        "scan_interval": scan_interval,
        "wishlist": ["title1", "title2"],
    }
    assert expected == hass.data[DOMAIN]["conf"]
    assert scan_interval == hass.data[DOMAIN]["coordinator"].update_interval
