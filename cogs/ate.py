import aiohttp
import ftfy
from bs4 import BeautifulSoup
from disnake.ext import commands

import embed_maker

ADVISORS = [[], [], []]


async def update_ate():
    global ADVISORS
    ADVISORS = [[], [], []]
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://steamcommunity.com/workshop/filedetails/discussion/2737385499/4944391335293065029/") as r:
            tree = await r.read()
    soup = BeautifulSoup(tree, "html.parser")
    container = soup.find(id="forum_op_4944391335293065029")
    titles = container.find_all("div", class_="bb_h1")
    i = 3
    for title in titles:
        if title.contents[0] == "Administrative Advisors":
            i = 0
        elif title.contents[0] == "Diplomatic Advisors":
            i = 1
        elif title.contents[0] == "Military Advisors":
            i = 2
        else:
            ADVISORS[i].append(title.contents[0])
    ADVISORS[0], ADVISORS[1], ADVISORS[2] = (
        sorted(ADVISORS[0]),
        sorted(ADVISORS[1]),
        sorted(ADVISORS[2]),
    )


class ATE(commands.Cog):
    """Advisor Types Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Great Monuments Expanded")
    async def ate(self, inter):
        pass

    @ate.sub_command(description="Steam Page")
    async def steam(self, inter):
        """Returns ATE steam page"""
        ate_embed = embed_maker.EmbedMaker(
            "Advisor Type Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=2737385499",
            "Better Advisors for everyone!",
            0xD5000,
            "Made by Limonen",
            "https://steamuserimages-a.akamaihd.net/ugc/1862803609355016327/D62CFAEABE72FB756FE7BBBC03D235BD78395BFB/",
        )
        await inter.send(embed=ate_embed.embed)

    @ate.sub_command(description="Gives a link for even more advisor types info")
    async def info(self, inter):
        ate_embed_info = embed_maker.EmbedMaker(
            "Advisor Type Expanded",
            "https://steamcommunity.com/workshop/filedetails/discussion/2737385499/4944391335293065029",
            "Additional Information!",
            0xD5000,
            "Made by Limonen",
            "https://steamuserimages-a.akamaihd.net/ugc/1862803609355016327/D62CFAEABE72FB756FE7BBBC03D235BD78395BFB/",
        )
        await inter.send(embed=ate_embed_info.embed)

    @ate.sub_command(description="Search for a specific advisor")
    async def find(self, inter):
        # await update_ate()
        await inter.send('Sorry, this command has not been implemented yet. Please use `+ate info` and "Ctrl + F" for the time being.')
        # Descriptions are hard to scrape in bullet form, so this still needs json files

        # with open('./data/ATE.json', 'r') as f:
        # 	ateData = json.load(f)

        # with open('./data/ATE_descriptions.json', 'r') as f:
        # 	ateDataDescription = json.load(f)

        # try:
        # 	ateBodyMessage = f'```{ateDataDescription[advisor]} \n---------\n'
        # 	for key, values in ateData[advisor].items():
        # 		ateBodyMessage = ateBodyMessage + f'{key.title()}: {values} \n'
        # 	ateBodyMessage = ateBodyMessage + '```'
        # 	await inter.send(ateBodyMessage)
        # except Exception:
        # 	await inter.send('Pizza couldn\'t find it T~T')

    @ate.sub_command(description="Show list of all Administrative Advisors in ATE")
    async def adm(self, inter):
        await update_ate()
        message = "```"
        for advisor in ADVISORS[0]:
            message += f"\u203B {advisor}\n"
        message += "```"
        await inter.send(ftfy.fix_text(message))

    @ate.sub_command(description="Show list of all Diplomatic Advisors in ATE")
    async def dip(self, inter):
        await update_ate()
        message = "```"
        for advisor in ADVISORS[1]:
            message += f"\u203B {advisor}\n"
        message += "```"
        await inter.send(ftfy.fix_text(message))

    @ate.sub_command(description="Show list of all Military Advisors in ATE")
    async def mil(self, inter):
        await update_ate()
        message = "```"
        for advisor in ADVISORS[2]:
            message += f"\u203B {advisor}\n"
        message += "```"
        await inter.send(ftfy.fix_text(message))


def setup(bot):
    bot.add_cog(ATE(bot))
