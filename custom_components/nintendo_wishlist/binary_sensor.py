import logging
from typing import List

from homeassistant import core
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.util import slugify

from .const import DOMAIN
from .types import SwitchGame


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: core.HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    _LOGGER.warning("setting up binary sensor")
    coordinator = hass.data[DOMAIN]["coordinator"]
    sensors = []
    for term in self.hass.data[DOMAIN]["conf"]["wishlist"]:
        sensors.append(SwitchGameQueryEntity(coordinator, term))
    async_add_entities(sensors, True)


class SwitchGameQueryEntity(BinarySensorDevice):
    """Represents a Query for a switch game."""

    def __init__(self, coordinator, game_title: str):
        self.attrs = {}
        self.coordinator = coordinator
        self.game_title = game_title
        self.matches: List[SwitchGame] = []

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return "mdi:nintendo-switch"

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
        return f"binary_sensor.nintendo_wishlist_{slug}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.game_title

    @property
    def device_state_attributes(self):
        return {"matches": self.matches}
