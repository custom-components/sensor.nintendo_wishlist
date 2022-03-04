import logging
from typing import List

from homeassistant import core
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import slugify

from .const import DOMAIN
from .types import EShopResults, SwitchGame

try:
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:
    # Prior to HA 0.110
    from homeassistant.components.binary_sensor import (
        BinarySensorDevice as BinarySensorEntity,
    )


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: core.HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    sensors = []
    for term in hass.data[DOMAIN]["conf"]["wishlist"]:
        sensors.append(SwitchGameQueryEntity(coordinator, term))
    async_add_entities(sensors, True)


class SwitchGameQueryEntity(CoordinatorEntity, BinarySensorEntity):
    """Represents a Query for a switch game."""

    def __init__(
        self, coordinator: DataUpdateCoordinator[EShopResults], game_title: str
    ):
        super().__init__(coordinator)
        self.attrs = {}
        self.game_title = game_title
        self.matches: list[SwitchGame] = []

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
    def extra_state_attributes(self):
        return {"matches": self.matches}
