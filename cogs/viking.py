import json

import ftfy
from disnake.ext import commands

import embed_maker


class VIKING(commands.Cog):
    """Viking Shattered Europa"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(case_insensitive=True)
    async def viking(self, ctx):
        """Returns the Viking steam page"""
        if ctx.invoked_subcommand is None:
            viking_embed = embed_maker.EmbedMaker(
                "Viking Shattered Europa",
                "https://steamcommunity.com/sharedfiles/filedetails/?id=2262234791",
                "A New World!",
                0xD5000,
                "Made by Viking",
                "https://steamuserimages-a.akamaihd.net/ugc/1791846904005809352/9EC1B055DBEC2D603CE17EC59FB0795F5D7F08FF/",
            )
            await ctx.send(embed=viking_embed.embed)

    @viking.command()
    async def find(self, ctx, *, country_in: str):
        """+viking find [tag] Sends back the nation with viking ideas"""
        with open("./debugging_tools/viking_json/Viking_country_ideas.json", "r", encoding="utf-8") as f:
            vik_data = json.load(f)
        with open("./data/tags/tagsVIK.json", "r", encoding="utf-8") as f:
            vik_tags = json.load(f)

        print(f"viking idea request received {country_in}")
        country_lst = country_in.split(",")
        for country in country_lst:
            country = country.strip()
            try:
                tag = country.upper()
                nation = vik_tags[tag]
            except Exception:
                try:
                    nation = country.title()
                    tag = list(vik_tags.keys())[list(vik_tags.values()).index(nation)]
                except Exception:
                    await ctx.send("Does your country have Bielefeld as a name? Pizza-chan is sure it doesn't exist oAo. If Pizza-chan is wrong, ping Melvasul or Vielor")
                    return

            try:
                vik_body_message = f"```Viking: {nation} Ideas \n---------\n"
                for key, values in vik_data[nation].items():
                    vik_body_message += f"{key.title()}: {values} \n"
                await ctx.send(ftfy.fix_text(f"{vik_body_message}```"))
            except Exception:
                await ctx.send("The country does not have VIKING ideas")

    @viking.command()
    async def countries(self, ctx):
        """Shows a list of all Countries in VIKING"""
        print("VIKING country list request received")
        with open("./debugging_tools/viking_json/Viking_country_ideas.json", "r", encoding="utf-8") as f:
            vik_data = json.load(f)

        message = "```"
        country_lst = sorted([key.title() for key in vik_data])

        for country in country_lst:
            if len(f"{message}{country}\n```") > 2000:
                await ctx.send(ftfy.fix_text(f"{message}```"))
                message = "```"
            message += f"{country}\n"
        await ctx.send(ftfy.fix_text(f"{message}```"))

    @viking.command(case_insensitive=True)
    async def country(self, ctx, *, tags_in: str):
        """Turns a tag into a country: +viking country ITA"""
        with open("./data/tags/tagsVIK.json", "r", encoding="utf-8") as f:
            vik_tags = json.load(f)
        message = ""
        tags_lst = tags_in.split(",")
        for tag in tags_lst:
            tag = tag.strip().upper()
            try:
                message += f"{vik_tags[tag]}\n"
            except Exception:
                message += f"{tag} doesn't exist oAo. If Pizza-chan is wrong, ping Melvasul or Vielor\n"
        await ctx.send(message)

    @viking.command(case_insensitive=True)
    async def tag(self, ctx, *, nations_in: str):
        """Turns a country in a tag: +viking tag Italy"""
        with open("./data/tags/tagsVIK.json", "r", encoding="utf-8") as f:
            vik_tags = json.load(f)
        message = ""
        nations = nations_in.split(",")
        for nation in nations:
            nation = nation.strip().title()
            try:
                message += f"{list(vik_tags.keys())[list(vik_tags.values()).index(nation)]}\n"
            except Exception:
                message += f"{nation} doesn't exist oAo. If Pizza-chan is wrong, ping Melvasul or Vielor\n"
        await ctx.send(message)


def setup(bot):
    bot.add_cog(VIKING(bot))
