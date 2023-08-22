import disnake
from disnake.ext import commands

import embed_maker


class HREE(commands.Cog):
    """Holy Roman Empire Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Great Monuments Expanded")
    async def hree(self, inter):
        pass

    @hree.sub_command(description="Steam Page")
    async def steam(self, inter):
        hree_embed = embed_maker.EmbedMaker(
            "Holy Roman Empire Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=1352521684",
            "Better Habsburg!",
            0xD5000,
            "Made by Lemon",
            "https://steamuserimages-a.akamaihd.net/ugc/1788469031561998021/B2EE97BB793DCF16E53467619DC3FD6EE0AAA834/",
        )
        await inter.send(embed=hree_embed.embed)

    @hree.sub_command(description="All releasable Duchies")
    async def duchies(self, inter):
        await inter.send(file=disnake.File(r"./data/images/duchies.png"))


def setup(bot):
    bot.add_cog(HREE(bot))
