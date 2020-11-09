import asyncio
import pprint

import aiohttp

from custom_components.nintendo_wishlist.eshop import EShop

WISHLIST = [
    "Super Mario Maker",
    "My Friend Pedro",
    "Timespinner",
    "Darkwood",
    "Aggelos",
    "Blaster Master Zero 2",
    "OlliOlli",
    "Shantae",
    "The Mummy Demastered",
    "Salt and Sanctuary",
    "Dead Cells",
    "Dark Souls",
    "Creature in the Well",
    "Spyro Reignited",
    "The Touryst",
    "Cadence of Hyrule",
    "Carrion",
    "Evergate",
    "Rock'N Racing Off Road DX",
    "Red Death",
    "Golem Gates",
]


async def main():
    async with aiohttp.ClientSession() as client:
        eshop = EShop("US", client, WISHLIST)
        games = await eshop.fetch_on_sale()
        pprint.pprint(games)
        print(len(games))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
