import json

import aiohttp
import bs4
from bs4 import BeautifulSoup
from disnake.ext import commands

import embed_maker


async def update_pte():
    """Updates PTE data"""
    data = {"Peace Treaties": [], "Casus Bellis": [], "State Edicts": [], "Covert Actions": []}

    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://steamcommunity.com/workshop/filedetails/discussion/2615504872/2961670721745264890/") as r:
            tree = await r.read()
    soup = BeautifulSoup(tree, "html.parser")
    container = soup.find(id="forum_op_2961670721745264890")
    titles = container.find_all("div", class_="bb_h1")
    i = ""
    for line in titles:
        if isinstance(line.contents[0], bs4.element.Tag):
            line = line.contents[0].contents[0].contents[0]

        if line in {"Peace Treaties", "Casus Bellis", "State Edicts", "Diplomatic Actions"}:
            i = line
            if i == "Diplomatic Actions":
                i = "Covert Actions"
        else:
            data[i].append(line.contents[0])
    with open("./data/pte_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


def get_pretty_lst(lst):
    """Returns a pretty list"""
    res = "```"
    for item in lst:
        res += f"\u203B {item}\n"
    return f"{res}```"


class PTE(commands.Cog):
    """Peace Treaties Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Peace Treaties Expanded")
    async def pte(self, inter):
        pass

    @pte.sub_command(description="Steam Page")
    async def steam(self, inter):
        pte_embed = embed_maker.EmbedMaker(
            "Peace Treaties Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=2615504872",
            "Westphalia, but better",
            0xD5000,
            "Made by Limonen",
            "https://steamuserimages-a.akamaihd.net/ugc/1635360679576009363/C07849AD1A7CFF64829E34D95C0062C16EC88056/",
        )
        await inter.send(embed=pte_embed.embed)

    @pte.sub_command(description="Gives a link for even more peace treaties info")
    async def info(self, inter):
        pte_embed_info = embed_maker.EmbedMaker(
            "Peace Treaties Expanded",
            "https://steamcommunity.com/workshop/filedetails/discussion/2615504872/2961670721745264890/",
            "Additional Information",
            0xFF2600,
            "All Peace Treaties explained",
            "https://steamuserimages-a.akamaihd.net/ugc/1635360679576009363/C07849AD1A7CFF64829E34D95C0062C16EC88056/",
        )
        await inter.send(embed=pte_embed_info.embed)

    @pte.sub_command(description="All Peace Treaties")
    async def treaties(self, inter):
        await update_pte()
        with open("./data/pte_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        result = get_pretty_lst(data["Peace Treaties"])
        await inter.send(result)

    @pte.sub_command(description="All Casus Belli")
    async def cb(self, inter):
        await update_pte()
        with open("./data/pte_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        result = get_pretty_lst(data["Casus Bellis"])
        await inter.send(result)

    @pte.sub_command(description="All State Edicts")
    async def edicts(self, inter):
        await update_pte()
        with open("./data/pte_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        result = get_pretty_lst(data["State Edicts"])
        await inter.send(result)

    @pte.sub_command(description="All Covert Actions")
    async def covert(self, inter):
        await update_pte()
        with open("./data/pte_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        result = get_pretty_lst(data["Covert Actions"])
        await inter.send(result)


def setup(bot):
    bot.add_cog(PTE(bot))
