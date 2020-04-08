from typing import Any, Dict, List

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .types import SwitchGame


class NintendoWishlistEntity(Entity):
    """Representation of a sensor."""

    def __init__(self, sensor_manager, wishlist: List[str]):
        self.attrs = {}
        self.coordinator = sensor_manager.coordinator
        self.wishlist = [g.lower() for g in wishlist]
        self._state = 0

    @property
    def entity_id(self):
        """Return the entity id of the sensor."""
        return "sensor.nintendo_wishlist"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Nintendo Wishlist"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def state(self):
        """Return the state of the sensor."""
        matches = self._parse_matches(list(self.coordinator.data.items()))
        self.attrs["on_sale"] = matches

        return len(matches)

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return "mdi:nintendo-switch"

    @property
    def device_state_attributes(self):
        return self.attrs

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    def _parse_matches(self, results: List[SwitchGame]) -> List[SwitchGame]:
        matches: List[SwitchGame] = []
        for game in results:
            if not game["title"].lower().startswith(tuple(self.wishlist)):
                continue
            matches.append(game)
        return matches
