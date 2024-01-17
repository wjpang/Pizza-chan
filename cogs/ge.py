import json

import disnake
import ftfy
from disnake.ext import commands

import embed_maker

color_map = {
    "Culture": "\u001B[0;33m",
    "Culture Group": "\u001B[0;33m",
    "Religion": "\u001B[0;33m",
    "Religion Group": "\u001B[0;33m",
    "Area": "\u001B[0;33m",
    "Is Year": "\u001B[0;33m",
}
stuff_to_color = [
    "Culture",
    "Culture Group",
    "Religion",
    "Religion Group",
    "Area",
    "Is Year",
]
pretty_lst = {
    "{": "[",
    "}": "]",
    ": \u001B[0;34mTrue\u001B[0;0m": "",
    "'": "",
    "[]": "\u001B[0;31mNone\u001B[0;0m",
}


class GE(commands.Cog):
    """Governments Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Governments Expanded")
    async def ge(self, inter):
        pass

    @ge.sub_command(description="Returns the GE steam page")
    async def steam(self, inter):
        ge_embed = embed_maker.EmbedMaker(
            "Governments Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=1596815683",
            "The best part of Dharma!",
            0xD5000,
            "Made by Jay and co.",
            "https://steamuserimages-a.akamaihd.net/ugc/794243175441321379/94E146928B3CA6CEA4A8762F72F3633DF8E9569D/",
        )
        await inter.send(embed=ge_embed.embed)

    @ge.sub_command(description="Gives a spreadsheet of all GE reforms")
    async def info(self, inter):
        await inter.send("https://eu4.paradoxwikis.com/Governments_Expanded")

    @ge.sub_command(description="Explains what are empowered reforms")
    async def empowered(self, inter):
        await inter.send(
            "Empowered reforms work similarly to rpg skill trees. Early generic reforms are "
            "available to all nations, but your choice will accrue you points in the following"
            " categories: Clergy/Burghers/Nobility/Royalty. After Tier 3, the combination of "
            "these points unlock hidden and stronger reforms."
        )

    @ge.sub_command(description="Raises war funds for Jay")
    async def patreon(self, inter):
        ge_patreon_embed = embed_maker.EmbedMaker(
            "Governments Expanded Patreon",
            "https://www.patreon.com/user?u=16752311/",
            "Support the developer!",
            0xD5000,
            "Made by Jay",
            "https://aescifi.ca/wp/wp-content/uploads/2019/05/Patreon-Icon.png/",
        )
        await inter.send(embed=ge_patreon_embed.embed)

    @ge.sub_command(description="A review of regions with GE reforms")
    async def map(self, inter):
        await inter.send(
            "Blue: S-tier\nYellow: A-tier\nRed: B-tier",
            file=disnake.File(r"./data/images/gemap.png"),
        )

    @ge.sub_command(description="search for either reforms, tiers or governments")
    async def find(self, inter, *, reform_in: str = commands.Param(name="reform")):
        indent = 0
        found = 0

        with open("./data/GE.json", "r", encoding="utf-8") as f:
            ge_data = json.load(f)
        government_lst = sorted(ge_data.keys())

        reform_list = reform_in.split(",")

        for reform in reform_list:
            found = 0
            reform = reform.strip().title()
            if reform in government_lst:  # used to search for Monarchy, Republic, etc
                message = f"```ansi\n\u001B[0;33m{reform}:\u001B[0;0m\n---------\n"
                for government in ge_data[reform]:
                    message += f"{government}\n"
                await inter.send(f"{message}```")
                continue
            else:
                for government in government_lst:  # used to search specific tiers
                    if found == 1:
                        break
                    tier_lst = sorted(ge_data[government].keys())
                    if reform in tier_lst:
                        found = 1
                        message = f"```ansi\n\u001B[0;33m{reform}:\u001B[0;0m\n---------\n"
                        for tier in sorted(ge_data[government][reform].keys()):
                            message += f"{tier}\n"
                        await inter.send(f"{message}```")
                        break
                    else:
                        for tier in tier_lst:
                            reform_lst = sorted(ge_data[government][tier].keys())
                            if reform in reform_lst:
                                found = 1
                                message = f"```ansi\n\u001B[0;33m{reform}:\u001B[0;0m\n---------\n"
                                for stats, vals in ge_data[government][tier][reform].items():
                                    if isinstance(vals, dict) and stats not in ("Effect", "Removed Effect"):
                                        message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m:\n"
                                        message += build_message(vals, indent + 1, stuff_to_color)
                                    else:
                                        message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m \n"
                                    for old, new in pretty_lst.items():
                                        message = message.replace(old, new)
                                await inter.send(f"{message}```")
                                break
            if found == 0:
                await inter.send(f"The searched government/tier/reform: {reform} does not exist in GE")

    # @ge.sub_command(description="GE find [reform] Finds a GE reform")
    # async def find(self, inter, *, arg: str):
    #     try:
    #         body_message = ""
    #         govs = ["Monarchy", "Republic", "Theocracy", "Tribal"]
    #         for gov in govs:
    #             for tier in ge_data[gov]:
    #                 for reform in ge_data[gov][tier]:
    #                     if arg in ge_data[gov][tier]:
    #                         img = ge_data[gov][tier][reform]["Image"]
    #                         pic = f"https://eu4.paradoxwikis.com{img}"
    #                         link = f"https://eu4.paradoxwikis.com/Governments_Expanded/{gov}"
    #                         for key, val in ge_data[gov][tier][arg]["Effects"].items():
    #                             body_message += f"{key}: {val}\n"
    #                         ge_reform_embed = embed_maker.EmbedMaker(
    #                             "More info here",
    #                             link,
    #                             body_message,
    #                             0xD5000,
    #                             "Made by Jay",
    #                             pic,
    #                         )
    #                         await inter.send(embed=ge_reform_embed.embed)
    #                         return
    #                     else:
    #                         continue
    #     except Exception:
    #         await inter.send("Pizza error OAO call Melvasul or Vielor")

    @ge.sub_command(description="GE Liberalism")
    async def liberalism(self, inter):
        message = (
            "Liberalism is a new modifier added in Governments Expanded. It gives -10% "
            "development cost, -25% maximum absolutism, -10% idea cost and +1 tolerance of "
            "heretics and heathens at 100%. It represents how free the citizens in your nation"
            " are to live their lives, undisturbed by state intervention. You can only get it "
            "through Republican reforms, some of which might add additional modifiers to your "
            "Liberalism like the Capitalism mechanic, which allows you to get up to +25% goods"
            " produced as well!"
        )
        await inter.send(ftfy.fix_text(message))


def setup(bot):
    bot.add_cog(GE(bot))


def build_message(data, indent=0, stuff_to_color=None):
    message = ""
    for stats, vals in data.items():
        if isinstance(vals, dict) and stats.title():
            message += "\t" * indent + f"{stats}:\n".title()
            message += build_message(vals, indent + 1, stuff_to_color)
        elif isinstance(vals, list) and stats.title():
            for item in vals:
                if isinstance(item, dict):
                    message += "\t" * indent + f"{stats}:\n".title()
                    message += build_message(item, indent + 1, stuff_to_color)
                elif isinstance(item, str):
                    message += "\t" * indent + f"{stats}: {vals} \n".title()
                    break
        elif stats in stuff_to_color:
            color = color_map.get(stats, "")
            message += "\t" * indent + f"{color}{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m\n"
        else:
            message += "\t" * indent + f"{stats}: \u001B[0;34m{vals}\u001B[0;0m \n"

    return message
