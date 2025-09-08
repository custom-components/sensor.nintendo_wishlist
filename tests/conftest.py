"""pytest fixtures."""

from unittest.mock import Mock

from aioresponses import aioresponses
import pytest

# @pytest.fixture(autouse=True)
# def auto_enable_custom_integrations(enable_custom_integrations):
#    """Enable custom integrations defined in the test dir."""
#    yield


@pytest.fixture
def mock_aioresponse():
    """Fixture to mock aiohttp calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def coordinator_mock(hass):
    """Fixture to mock the update data coordinator."""
    coordinator = Mock(data={}, hass=hass)
    coordinator.data = {
        70010000012683: {
            "box_art_url": "https://www.nintendo.com/content/dam/noa/en_US/games/switch/a/aggelos-switch/Switch_Aggelos_box_eShop.png",
            "normal_price": 14.99,
            "nsuid": 7001000012683,
            "percent_off": 45,
            "sale_price": 8.24,
            "title": "Aggelos",
        }
    }
    yield coordinator
