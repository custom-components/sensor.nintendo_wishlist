from __future__ import annotations

from typing import TypedDict


class SwitchGame(TypedDict):
    box_art_url: str
    normal_price: str | None
    nsuid: int
    percent_off: float
    sale_price: str | None
    title: str


class ResultsDict(TypedDict):
    games: dict[int, SwitchGame]
    num_pages: int


EShopResults = dict[int, SwitchGame]
