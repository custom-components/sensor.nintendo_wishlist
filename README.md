# Nintendo Wishlist Component

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## NOTE: This component currently only works in certain countries.  See [Supported Countries](#supported-countries) below.

Home Assistant component that keeps track of Nintendo Switch games that are on
sale on your wish list in home assistant. (There is currently not a way to get your
wish list from Nintendo, so you have to keep track of it in this component.)

[![nitendo wishlist card](https://raw.githubusercontent.com/custom-cards/nintendo-wishlist-card/master/cover-art.png)](https://raw.githubusercontent.com/custom-cards/nintendo-wishlist-card/master/cover-art.png)

## HACS Installation

1. Search for `Nintendo Wishlist Component` in the HACS Store tab.
2. Add the code to your `configuration.yaml` using the config options below.
3. **You will need to restart after installation for the component to start working.**
4. Display it in your lovelace UI using the [nintendo-wishlist-card](https://github.com/custom-cards/nintendo-wishlist-card).

## Platform Configuration

|Name|Required|Description|
|-|-|-|
|country|yes|The 2 letter country code.  See [Supported Countries](#supported-countries) below.|
|whishlist|yes|A list of Nintendo Switch titles|

## Sample Sensor Configuration

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

### Supported Countries

|Country Code|Country Name|
|-|-|
|AT|Austria|
|BE|Belgium|
|CA|Canada|
|CH|Schweiz/Suisse/Svizzera|
|DE|Germany|
|ES|Spain|
|FR|France|
|GB|UK/Ireland|
|IT|Italy|
|NL|Netherlands|
|PT|Portugal|
|RU|Russia|
|US|United States|
|ZA|South Africa|


### How wish list matching works

Currently wish list matching uses a very simple string comparison.  It's
possible to get false positives as it checks to see if any game on your wish
list starts with any title that is on sale.  In order to avoid false positives
try to have the title match that on the nintendo e-store as closely as possible.

Conversely, if you would like to match multiple titles that have a similar name
you can specify less of the title.  An example of this would be to add an item
to your wishlist like `Shantae`.  This would match any of the Shantae titles on
the e-shop (e.g. `Shantae and the Pirate's Curse` and `Shantae: Half-Genie Hero`.

### Sensors for Automations

When the custom component is run it will create a new sensor named `sensor.nintendo_wishlist`.
It's state will be the total number of games from your wish list that are on sale.
This sensor can be used with the [custom card](https://github.com/custom-cards/nintendo-wishlist-card).

The component will additionally create a sensor per title in your wish list.  These
will be named `sensor.nintendo_wishlist_{title_name}`.  For example Mega Man 11
would be `sensor.nintendo_wishlist_mega_man_11`.  The state of each sensor will
be `0` if it is not on sale and `1` if it is on sale.  You can use these sensors
in your automations to send notifications, blink your lights, or any other
automation you would like to do when a title on your wish list goes on sale.

[![example sensors](https://raw.githubusercontent.com/custom-components/sensor.nintendo_wishlist/master/sensors.png)](https://raw.githubusercontent.com/custom-components/sensor.nintendo_wishlist/master/sensors.png)

#### Example NodeRed Flow

You can import an [example of a node-red flow](https://raw.githubusercontent.com/custom-components/sensor.nintendo_wishlist/master/example_node_red_flow.json) that sends an alert to kodi when
a game on your wish list is on sale.  You can use the inject node to test the
flow and customize it to your preferences.

[![example nodered flow](https://raw.githubusercontent.com/custom-components/sensor.nintendo_wishlist/master/example_node_red_flow.png)](https://raw.githubusercontent.com/custom-components/sensor.nintendo_wishlist/master/example_node_red_flow.png)
