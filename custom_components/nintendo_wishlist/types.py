from typing import Any, Dict, Optional

from typing_extensions import TypedDict


class SwitchGame(TypedDict):
    box_art_url: str
    normal_price: Optional[str]
    nsuid: int
    percent_off: float
    sale_price: Optional[str]
    title: str


class ResultsDict(TypedDict):
    games: Dict[int, SwitchGame]
    num_pages: int


EShopResults = Dict[int, SwitchGame]
