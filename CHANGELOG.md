# CHANGELOG

## v2.2.0 (2019-12-24)

* Updated to parse all games on sale.  Previously it was only looking at
  the first 350 results so it's possible it would miss finding a game on your
  wish list.

## v2.1.1 (2019-08-12)

* Updated the friendly name for each created sensor to just be the game title.

## v2.1.0 (2019-08-04)

* Added a sensor for each game in the wish list in addition to the previous
  sensor that contained all games on the wish list.

## v2.0.3 (2019-08-01)

* Increase the number of search results to 350 as we weren't looking at all
  games on sale (only the first 250 and there were 306 results).

## v2.0.2 (2019-07-31)

* Fixed bug that caused an error for certain countries (Schweiz, Ireland, UK,
  and Belgium).

## v2.0.1 (2019-07-30)

* Fixed bug where non North American countries would show the `$` in the price
  along with the local currency.

## v2.0.0 (2019-07-23)

* `country` is now required in the sensor platform configuration.
* Now supports 12 other countries.
