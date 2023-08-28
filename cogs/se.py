import json

import aiohttp
from bs4 import BeautifulSoup
from disnake.ext import commands

import embed_maker


async def update_se():
    """Updates SE data"""
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://steamcommunity.com/workshop/filedetails/discussion/1834079712/3647273545685194210/") as r:
            tree = await r.read()
    soup = BeautifulSoup(tree, "html.parser")
    data = dict(
        zip(
            [subject.contents[0] for subject in soup.find(id="forum_op_3647273545685194210").find_all("div", class_="bb_h1")],
            [desc.contents[0] for desc in soup("i")],
        )
    )
    with open("./data/se_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


class SE(commands.Cog):
    """Subjects Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Subjects Expanded")
    async def se(self, inter):
        pass

    @se.sub_command(description="Steam Page")
    async def steam(self, inter):
        se_embed = embed_maker.EmbedMaker(
            "Subjects Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=1834079712",
            "For all your overlording needs",
            0xD5000,
            "Made by Lemon",
            "https://steamuserimages-a.akamaihd.net/ugc/791991207699275639/21257382F358B5F2A6226827AC891A22BAC2C901/",
        )
        await inter.send(embed=se_embed.embed)

    @se.sub_command(description="Finds info on a specific subject")
    async def find(self, inter, *, subject: str):
        await update_se()
        with open("./data/se_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            if subject.title() == "Dar Al-Sulh Territory":
                subject = "Dar al-Sulh Territory"
            elif subject.title() in {"Stato Da Màr", "Stato Da Mar"}:
                subject = "Stato da Màr"
            else:
                subject = subject.title()
            await inter.send(data[subject])
        except Exception:
            await inter.send("Pizza-chan can't find it")

    @se.sub_command(description="List of all subjects")
    async def subjects(self, inter):
        await update_se()
        with open("./data/se_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.keys()
        subject_lst = sorted(title)
        result = "```"
        for subject in subject_lst:
            result += f"\u203B {subject}\n"
        await inter.send(f"{result}```")

    @se.sub_command(description="Gives a link for even more subject info")
    async def info(self, inter):
        se_embed_info = embed_maker.EmbedMaker(
            "Subjects Expanded",
            "https://steamcommunity.com/workshop/filedetails/discussion/1834079712/3647273545685194210/",
            "See the Details",
            0xD5000,
            "All Subject Data",
            "https://steamuserimages-a.akamaihd.net/ugc/791991207699275639/21257382F358B5F2A6226827AC891A22BAC2C901/",
        )
        await inter.send(embed=se_embed_info.embed)


def setup(bot):
    bot.add_cog(SE(bot))
