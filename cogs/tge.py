import json

import disnake
from disnake.ext import commands

import embed_maker


class TGE(commands.Cog):
    """Trade Goods Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Trade Goods Expanded")
    async def tge(self, inter):
        pass

    @tge.sub_command(description="Steam Page")
    async def steam(self, inter):
        tge_embed = embed_maker.EmbedMaker(
            "Trade Goods Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=1770950522",
            "Actual Trade!",
            0xD5000,
            "Made by MrMarcinQ",
            "https://steamuserimages-a.akamaihd.net/ugc/772854714567526593/6B51AC8E47D22DBC610D70168E929F6CAD3A3F1C/",
        )
        await inter.send(embed=tge_embed.embed)

    @tge.sub_command(description="Finds a specific TGE good (+tge find [good])")
    async def find(self, inter, *, goods_list: str = commands.Param(name="good")):
        with open("data/TGE.json", "r", encoding="utf-8") as f:
            tge_goods = json.load(f)

        for good in goods_list.split(","):
            good = good.strip().title()
            if good == "Silver":
                await inter.send(
                    "Silver is a special trade good that works exactly like Gold. The only difference is its ducat conversion rate. The rate is 28 ducats per year per unit of goods produced."
                )
                continue
            try:
                message = f"Price: {tge_goods[good]['Price']}\n" f"Trade leader bonus: {tge_goods[good]['Trade leader bonus']}\nProvince bonus: {tge_goods[good]['Province bonus']}"
                root = "./data/tge_images/"
                if len(good.split()) > 1:
                    picture = f"{root}{'_'.join(good.lower().split())}.png"
                else:
                    picture = f"{root}{good.lower()}.png"
                tge_good_embed = embed_maker.EmbedMaker("More info here", "https://eu4.paradoxwikis.com/Trade_Goods_Expanded/", message, 0xD50000, good, picture)
                await inter.send(embed=tge_good_embed.embed)
            except IndexError:
                await inter.send("No such good exists!")

    @tge.sub_command(description="Gives back a list of all TGE trade goods")
    async def goods(self, inter):
        with open("data/TGE.json", "r", encoding="utf-8") as f:
            tge_goods = json.load(f)
        tge_data = sorted(list(tge_goods.keys()) + ["Silver"])
        message = "```"
        for good in tge_data:
            message += f"\u203B {good}\n"
        await inter.send(f"{message}```")

    @tge.sub_command(description="Concerning why Navarra has whaling as a trade good")
    async def navarra(self, inter):
        await inter.send("1. The Basque region was known for whaling.\n2. This is PDX's fault since they redrew their map borders.\n3. Navarra was not landlocked historically.")

    @tge.sub_command(description="Shows a map of all starting trade goods")
    async def map(self, inter):
        await inter.send(file=disnake.File("./data/images/tgemap.png"))

    @tge.sub_command(description="Gives a link to the TGE wiki")
    async def wiki(self, inter):
        await inter.send("https://eu4.paradoxwikis.com/Trade_Goods_Expanded")


def setup(bot):
    bot.add_cog(TGE(bot))
