import logging
from typing import List

from homeassistant import core
from homeassistant.helpers.entity import Entity

from .const import CONF_WISHLIST, DOMAIN
from .types import SwitchGame


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: core.HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    _LOGGER.warning("setting up sensor")
    coordinator = hass.data[DOMAIN]["coordinator"]
    wishlist = hass.data[DOMAIN]["conf"][CONF_WISHLIST]
    async_add_entities([NintendoWishlistEntity(coordinator, wishlist)], True)


class NintendoWishlistEntity(Entity):
    """Representation of a sensor."""

    def __init__(self, coordinator, wishlist: List[str]):
        self.attrs = {}
        self.coordinator = coordinator
        self.wishlist = [g.lower() for g in wishlist]
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
