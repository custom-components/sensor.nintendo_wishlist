import logging
from typing import Callable

from homeassistant import core
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import async_get_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .eshop import EShop


_LOGGER = logging.getLogger(__name__)
WISHLIST_ID = -1


class NintendoWishlistDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for all nintendo_wishlist entities.

    This class handles updating for all entities created by this component.
    Since all data required to update all sensors and binary_sensors comes
    from a single api endpoint, this will handle fetching that data.  This way
    each entity doesn't need to fetch the exact same data every time an update
    is scheduled.
    """

    def __init__(self, hass: core.HomeAssistant, eshop: EShop):
        self.eshop = eshop
        self.http_session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_fetch_data,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_fetch_data(self):
        """Fetch the data for the coordinator."""
        return await self.eshop.fetch_on_sale()

    @callback
    def async_add_listener(
        self, update_callback: core.CALLBACK_TYPE
    ) -> Callable[[], None]:
        """Listen for data updates.

        @NOTE: this is copied from an unreleased version of HA (v0.108.0).  After that
        Release we may be able to use this (and set the minimum version in hasc.json to
        0.108.0)
        """
        schedule_refresh = not self._listeners

        self._listeners.append(update_callback)

        # This is the first listener, set up interval.
        if schedule_refresh:
            self._schedule_refresh()

        @callback
        def remove_listener() -> None:
            """Remove update listener."""
            self.async_remove_listener(update_callback)

        return remove_listener


class SensorManager:
    def __init__(self, hass: core.HomeAssistant):
        self.hass = hass
        # self.coordinator = coordinator  # @TODO:
