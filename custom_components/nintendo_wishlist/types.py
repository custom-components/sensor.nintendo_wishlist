from typing import Optional

from typing_extensions import TypedDict


class SwitchGame(TypedDict):
    box_art_url: str
    normal_price: str
    percent_off: float
    sale_price: str
    title: str
