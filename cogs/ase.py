import json

import disnake
import ftfy
from disnake.ext import commands

import embed_maker


class ASE(commands.Cog):
    """Ages and Splendor Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Ages and Splendor Expanded")
    async def ase(self, inter):
        pass

    @ase.sub_command(description="Steam Page")
    async def steam(self, inter):
        """Returns the ASE steam page"""
        ase_embed = embed_maker.EmbedMaker(
            "Ages and Splendor Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=2172666098",
            "We have Ages!",
            0xD5000,
            "Made by Melvasul and co.",
            "https://steamuserimages-a.akamaihd.net/ugc/1455177151331418092/0F4DB958BCA9F63CBC5B03EFCFCDBBE88093CEF5/",
        )
        await inter.send(embed=ase_embed.embed)

    @ase.sub_command(description="You can only search entire Ages")
    async def find(self, inter, *, age: str):
        age = age.title()
        with open("./data/ASE.json", "r", encoding="utf-8") as f:
            ase_data = json.load(f)

        try:
            ase_body_message = f"```Age of {age} \n---------\n"
            for key, values in ase_data[age].items():
                ase_body_message += f"{key.title()}: {values} \n"
            ase_body_message += "```"
            pretty_lst = {
                "{": "[ ",
                "}": " ]",
                ": True": "",
                "'": "",
                "[]": "None",
                "---:": "---------",
                "----:": "---------",
            }
            for old, new in pretty_lst.items():
                ase_body_message = ase_body_message.replace(old, new)
            await inter.send(ftfy.fix_text(ase_body_message))
        except Exception:
            await inter.send("Pizza couldn't find it T~T")

    @ase.sub_command(description="You can only retain the generic abilities. The cost is 1600 Splendor.")
    async def retainers(self, inter, *, age: str):
        age = age.title()

        if age == "Discovery":
            await inter.send("This is possible only using Extended Timeline")
        elif age == "Reformation":
            await inter.send(
                "In the Age of Reformation you will have a decision allowing you to choose ONE of the Age of Discovery Abilities as a permanent modifier",
                file=disnake.File(r"./data/images/ARDiscovery.png"),
            )
        elif age == "Absolutism":
            await inter.send(
                "In the Age of Absolutism the decision will allow you to choose one of the Age of Reformation Generic Abilities as a permanent modifier",
                file=disnake.File(r"./data/images/ARReformation.png"),
            )
        elif age == "Revolutions":
            await inter.send(
                "In the Age of Revolutions the decision will enable to choose one of the Age of Absolutism Generic Abilities as a permanent modifier",
                file=disnake.File(r"./data/images/ARAbsolutism.png"),
            )
        else:
            await inter.send("Please insert a valid Age between the 4 vanilla ones")


def setup(bot):
    bot.add_cog(ASE(bot))
