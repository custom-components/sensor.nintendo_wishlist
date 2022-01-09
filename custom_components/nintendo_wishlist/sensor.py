import logging

from homeassistant import core
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .types import EShopResults

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: core.HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([NintendoWishlistEntity(coordinator)], True)


class NintendoWishlistEntity(CoordinatorEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator[EShopResults]):
        super().__init__(coordinator)
        self.attrs = {}
        self._state = 0

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return "mdi:nintendo-switch"

    @property
    def entity_id(self):
        """Return the entity id of the sensor."""
        return "sensor.nintendo_wishlist"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Nintendo Wishlist"

    @property
    def state(self):
        """Return the state of the sensor."""
        matches = list(self.coordinator.data.values())
        self.attrs["on_sale"] = matches
        return len(matches)

    @property
    def extra_state_attributes(self):
        return self.attrs
