import logging

from typing import Any, Dict, List

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .types import SwitchGame


_LOGGER = logging.getLogger(__name__)


class BaseEntity(Entity):
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return "mdi:nintendo-switch"

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class NintendoWishlistEntity(BaseEntity):
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
    def state(self):
        """Return the state of the sensor."""
        matches = self._parse_matches(list(self.coordinator.data.values()))
        self.attrs["on_sale"] = matches

        return len(matches)

    @property
    def device_state_attributes(self):
        return self.attrs

    def _parse_matches(self, results: List[SwitchGame]) -> List[SwitchGame]:
        matches: List[SwitchGame] = []
        for game in results:
            if not game["title"].lower().startswith(tuple(self.wishlist)):
                continue
            matches.append(game)
        return matches


class SwitchGameQueryEntity(BaseEntity, BinarySensorDevice):
    """Represents a Query for a switch game."""

    def __init__(self, sensor_manager, game_title: str):
        self.attrs = {}
        self.coordinator = sensor_manager.coordinator
        self.game_title = game_title
        self.matches: List[SwitchGame] = []

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        matches = []
        for game in self.coordinator.data.values():
            if game["title"].lower().startswith(self.game_title.lower()):
                matches.append(game)
        self.matches = matches
        _LOGGER.warning("found %s matches for term %s", matches, self.game_title)
        return len(self.matches) > 0

    @property
    def entity_id(self) -> str:
        """Return the entity id of the sensor."""
        slug = slugify(self.game_title)
        return f"binary_sensor.steam_wishlist_{slug}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.game_title

    @property
    def device_state_attributes(self):
        return {"matches": self.matches}
