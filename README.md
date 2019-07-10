# Nintendo Wishlist Component

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## NOTE: This component currently only works with the US e-shop.

Home Assistant component that keeps track of Nintendo Switch games that are on
sale on your wish list in home assistant. (There is currently not a way to get your
wish list from Nintendo, so you have to keep track of it in this component.)

## HACS Installation

1. Search for `Nintendo Wishlist Component` in the HACS Store tab.
2. Add the code to your `configuration.yaml` using the config options below.
3. **You will need to restart after installation for the component to start working.**

## Sample Sensor Configuration

    sensor:
    - platform: nintendo_wishlist
      wishlist:
        - Katana ZERO
        - OKAMI HD
        - Salt and Sanctuary
        - Dead Cells
        - Bloodstained
        - Dark Souls
        - Velocity X

### How wish list matching works

Currently wish list matching uses a very simple string comparison.  It's
possible to get false positives as it checks to see if any game on your wish
list starts with any title that is on sale.  In order to avoid false positives
try to have the title match that on the nintendo e-store as closely as possible.

Conversely, if you would like to match multiple titles that have a similar name
you can specify less of the title.  An example of this would be to add an item
to your wishlist like `Shantae`.  This would match any of the Shantae titles on
the e-shop (e.g. `Shantae and the Pirate's Curse` and `Shantae: Half-Genie Hero`.
