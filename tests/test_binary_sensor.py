"""Test the SwitchGameQueryEntity."""
from custom_components.nintendo_wishlist.binary_sensor import SwitchGameQueryEntity


async def test_entity_is_on(coordinator_mock):
    """Test the is_on property of the entity."""
    entity = SwitchGameQueryEntity(coordinator_mock, "Aggelos")
    assert entity.is_on is True

    entity = SwitchGameQueryEntity(coordinator_mock, "Resident Evil")
    assert entity.is_on is False


def test_entity_id(coordinator_mock):
    """Test the entity_id property."""
    entity = SwitchGameQueryEntity(coordinator_mock, "Aggelos")
    assert "binary_sensor.nintendo_wishlist_aggelos" == entity.entity_id


def test_static_properties(coordinator_mock):
    """Test the entity_id property."""
    entity = SwitchGameQueryEntity(coordinator_mock, "Aggelos")
    assert "on sale" == entity.unit_of_measurement
    assert "mdi:nintendo-switch" == entity.icon
    assert "Aggelos" == entity.name
    assert {"matches": []} == entity.extra_state_attributes
