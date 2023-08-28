import json

import ftfy
from disnake.ext import commands

import embed_maker


def message_maker(advisor, mp, advisors):
    message = f"```{advisor} ({mp})\n----------\n"
    for modifier, value in advisors[advisor].items():
        if modifier == "Skill Scaled Modifier":
            message += f"{modifier}:\n"
            for mod, val in value.items():
                message += f"\t{mod}: {val}\n"
        else:
            message += f"{modifier}: {value}\n"
    message += "```\n"
    return message


class ATE(commands.Cog):
    """Advisor Types Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Advisor Types Expanded")
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
    async def find(self, inter, *, advisor_in: str = commands.Param(name="advisor")):
        with open("./data/ATE.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        advisor_lst = advisor_in.split(",")
        message = ""
        for advisor in advisor_lst:
            advisor = advisor.strip().title()
            if advisor == "Imperial Bureaucrat":
                message += "Imperial Bureaucrat provides only 0.1 Yearly Meritocracy (scaled with Advisor's level), as opposed to vanilla's normal 0.25 Yearly Meritocracy.\n"
            if advisor == "Loyal Friend":
                for mp, advisors in data.items():
                    temp = message_maker(advisor, mp, advisors)
                    if len(f"{message}{temp}") > 2000:
                        await inter.send(ftfy.fix_text(message))
                        message = ""
                    message += temp
                continue
            found = 0
            for mp, advisors in data.items():
                if advisor in advisors.keys():
                    found = 1
                    temp = message_maker(advisor, mp, advisors)
                    if len(f"{message}{temp}") > 2000:
                        await inter.send(ftfy.fix_text(message))
                        message = ""
                    message += temp
                    break
            if not found:
                message += f"{advisor} not found! If you think this is a mistake, ping Vielor or Melvasul.\n"

        await inter.send(ftfy.fix_text(message))

    @ate.sub_command(description="Show list of all Advisors in ATE")
    async def advisors(self, inter):
        with open("./data/ATE.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        message = ""
        for mp, advisors in data.items():
            message += f"**{mp.upper()}**\n"
            message += "```"
            for advisor in advisors.keys():
                message += f"\u203B {advisor}\n"
            message += "```\n"
        await inter.send(ftfy.fix_text(message))

    @ate.sub_command(description="Show list of all Administrative Advisors in ATE")
    async def adm(self, inter):
        with open("./data/ATE.json", "r", encoding="utf-8") as f:
            data = json.load(f)["ADM"]
        message = "```"
        for advisor in data.keys():
            message += f"\u203B {advisor}\n"
        message += "```"
        await inter.send(ftfy.fix_text(message))

    @ate.sub_command(description="Show list of all Diplomatic Advisors in ATE")
    async def dip(self, inter):
        with open("./data/ATE.json", "r", encoding="utf-8") as f:
            data = json.load(f)["DIP"]
        message = "```"
        for advisor in data.keys():
            message += f"\u203B {advisor}\n"
        message += "```"
        await inter.send(ftfy.fix_text(message))

    @ate.sub_command(description="Show list of all Military Advisors in ATE")
    async def mil(self, inter):
        with open("./data/ATE.json", "r", encoding="utf-8") as f:
            data = json.load(f)["MIL"]
        message = "```"
        for advisor in data.keys():
            message += f"\u203B {advisor}\n"
        message += "```"
        await inter.send(ftfy.fix_text(message))


def setup(bot):
    bot.add_cog(ATE(bot))
