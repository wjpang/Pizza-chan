from disnake.ext import commands

import embed_maker


class EMF(commands.Cog):
    """Expanded Mod Family"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Expaded Mod Family")
    async def emf(self, inter):
        pass

    @emf.sub_command(description="Steam Page")
    async def steam(self, inter):
        """Returns EMF steam page"""
        emf_embed = embed_maker.EmbedMaker(
            "Expanded Mod Family",
            "https://steamcommunity.com/workshop/filedetails/?id=1626860092",
            "Even more Mods!",
            0xD5000,
            "Made by a bunch of Cunts",
            "https://steamuserimages-a.akamaihd.net/ugc/773984225627222614/8177F29F3E27CFB8FE98D84E95469F0E48F5CD54/",
        )
        await inter.send(embed=emf_embed.embed)


def setup(bot):
    bot.add_cog(EMF(bot))
