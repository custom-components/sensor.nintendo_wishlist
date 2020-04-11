# Migration Guide to v3.0.0

There were a few breaking changes introduced in `v3.0.0`.  This guide will
document the changes and what you will need to fix to make the integration work
if you previously had an older version installed.

## Configuration

Before `v3.0.0` configuration was done as a platform.  This was changed to now
simply be a top level configuration in your `configuration.yaml`.  See the example
below of the old configuration and what it should look like in `v3.0.0`.

```yaml
# Old config prior to v3.0.0
sensor:
- platform: nintendo_wishlist
  country: US
  wishlist:
    - Katana ZERO
    - OKAMI HD
    - Salt and Sanctuary
    - Dead Cells
    - Bloodstained
    - Dark Souls
    - Velocity X
    - "The Legend of Zelda: Breath of the Wild"

# New config in v3.0.0
nintendo_wishlist:
  country: US
  wishlist:
    - Katana ZERO
    - OKAMI HD
    - Salt and Sanctuary
    - Dead Cells
    - Bloodstained
    - Dark Souls
    - Velocity X
    - "The Legend of Zelda: Breath of the Wild"
```

## Sensors

Prior to `v3.0.0` a `sensor` was created for each game in your wishlist.  It's
state would be `0` if it was not on sale and `1` if it was on sale.  Now instead
of a `sensors`, each game on your wishlist will create a `binary_sensor`.  The
state will be `true` if the game is on sale and `false` if it is not on sale.

### Attributes

The attribute `on_sale` for each `binary_sensor` on your wishlist was renamed to
`matches`.  If you have automations using the old `on_sale` attribute, you will
need to rename it to `matches`.
