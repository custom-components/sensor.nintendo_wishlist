import logging

from homeassistant import core
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: core.HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([NintendoWishlistEntity(coordinator)], True)


class NintendoWishlistEntity(Entity):
    """Representation of a sensor."""

    def __init__(self, coordinator):
        self.attrs = {}
        self.coordinator = coordinator
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
    def device_state_attributes(self):
        return self.attrs

    async def async_update(self):
        """Update the entity.

        This is only used by the generic entity update service. Normal updates
        happen via the coordinator.
        """
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Subscribe entity to updates when added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )
