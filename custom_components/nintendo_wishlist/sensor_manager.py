import logging
from typing import Callable, Dict, List

from homeassistant import core
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import async_get_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .eshop import EShop
from .entities import NintendoWishlistEntity, SwitchGameQueryEntity
from .types import SwitchGame


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
    def __init__(
        self,
        hass: core.HomeAssistant,
        coordinator: NintendoWishlistDataUpdateCoordinator,
    ):
        self.hass = hass
        self.coordinator = coordinator
        self._component_add_entities = {}
        self.registered = False

    async def async_register_component(
        self, platform: str, async_add_entities: Callable
    ):
        """Register a platform for the component."""
        self._component_add_entities[platform] = async_add_entities
        if len(self._component_add_entities) < 2:
            # Haven't registered both `sensor` and `binary_sensor` platforms yet.
            return

        # All platforms are now registered for the component.
        # Add callback to update sensors when coordinator refreshes data.
        _LOGGER.warning("registering components")
        self.coordinator.async_add_listener(self.async_update_items)
        # Fetch initial data.
        await self.coordinator.async_refresh()

    @callback
    def async_update_items(self):
        """Add or remove sensors based on coordinator data."""
        if self.registered:
            return
        _LOGGER.warning("async_update_items: %s", self._component_add_entities)
        if len(self._component_add_entities) < 2:
            # Haven't registered both `sensor` and `binary_sensor` platforms yet.
            return

        new_sensors: List[NintendoWishlistEntity] = []
        if not self.current_wishlist.get(WISHLIST_ID):
            wishlist = self.hass.data[DOMAIN]["conf"]["wishlist"]
            self.current_wishlist[WISHLIST_ID] = NintendoWishlistEntity(self, wishlist)
            new_sensors.append(self.current_wishlist[WISHLIST_ID])

        new_binary_sensors: List[SwitchGameQueryEntity] = []
        for term in self.hass.data[DOMAIN]["conf"]["wishlist"]:
            new_binary_sensors.append(SwitchGameQueryEntity(self, term))

        if new_sensors:
            self._component_add_entities["sensor"](new_sensors)
        if new_binary_sensors:
            self._component_add_entities["binary_sensor"](new_binary_sensors)
        self.registered = True
