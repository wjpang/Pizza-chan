import json

import disnake
from disnake.ext import commands

import embed_maker


def hie_special(country):
    """Filter for special HIE nations"""
    country = country.upper() if len(country) == 3 else country.title()
    if country in {"NED", "Netherlands", "Netherland"}:
        return (
            "NED",
            "Netherlands",
            ["-Dutch", "-Frisian", "-Flemish"],
        )
    if country in {"RUS", "Russia"}:
        return (
            "RUS",
            "Russia",
            ["-Muscovy", "-Novgorod"],
        )
    if country in {"PLC", "Commonwealth"}:
        return (
            "PLC",
            "Commonwealth",
            ["-Poland", "-Lithuania"],
        )
    if country in {"GRE", "Greece"}:
        return (
            "GRE",
            "Greece",
            ["-Greek", "-Latin"],
        )
    if country in {"KOJ", "Jerusalem"}:
        return (
            "KOJ",
            "Jerusalem",
            ["", "-Knights", "-Latin"],
        )
    if country in {"HLR", "Holy Roman Empire"}:
        return (
            "HLR",
            "Holy Roman Empire",
            ["", "-Burgundy", "-Bohemia", "-Habsburg", "-Latin"],
        )
    if country in {"GER", "Germany"}:
        return (
            "GER",
            "Germany",
            ["", "-Revolutionary"],
        )
    if country in {"COLONIAL", "Colonial"}:
        return (
            "COLONIAL",
            "Colonial",
            ["-British", "-Dutch", "-Latin", "-Portuguese", "-Spanish"],
        )
    return False


def ideas_message(mod, nation, data):
    """Creates the ideas message block for nation in mod"""
    message = f"```ansi\n\u001B[0;33m{mod.upper()}: {nation} Ideas\u001B[0;0m \n---------"
    for key, values in data[nation].items():
        if isinstance(values, dict):
            message += f"\n\u001B[0;33m{key.title()}\u001B[0;0m: "
            message += "{ "
            for k, v in values.items():
                message += f"{k.title()}: \u001B[0;34m{v}\u001B[0;0m, "
            message += "}"
        else:
            message += f"{key.title()}: \u001B[0;34m{values}\u001B[0;0m\n"
    pretty_lst = {
        ", }": " }",
    }
    for old, new in pretty_lst.items():
        message = message.replace(old, new)
    return f"{message}```"


def accessory(country):
    """Filter for country names with special chars"""
    if country in {
        "Alencon",
        "Luneburg",
        "Munster",
        "Leon",
        "Rum",
        "Sale",
        "Tetouan",
        "Fada Ngourma",
        "Lubeck",
        "Jenne",
        "Rugen",
        "Donauworth",
        "Osnabruck",
        "Oahu",
        "Kauai",
    }:
        return {
            "Alencon": "Alençon",
            "Luneburg": "Lüneburg",
            "Munster": "Münster",
            "Leon": "León",
            "Rum": "Rûm",
            "Sale": "Salé",
            "Tetouan": "Tétouan",
            "Fada Ngourma": "Fada N'gourma",
            "Lubeck": "Lübeck",
            "Jenne": "Jenné",
            "Rugen": "Rügen",
            "Donauworth": "Donauwörth",
            "Osnabruck": "Osnabrück",
            "Oahu": "O'ahu",
            "Kauai": "Kaua'i",
        }[country]
    return False


def country_filter(country, tags):
    """Filter for country names of length 3"""
    if len(country) != 3:
        return list(tags.keys())[list(tags.values()).index(country)], country
    if country in {"Sus", "Chu", "Zia", "Lau", "Han", "Sui", "Wei", "Xia", "Rûm"}:
        return (
            {
                "Sus": "SOS",
                "Chu": "CHC",
                "Zia": "KER",
                "Lau": "LAI",
                "Han": "ZHA",
                "Sui": "ZSU",
                "Wei": "ZWE",
                "Xia": "ZXI",
                "Rûm": "RUM",
            }[country],
            country,
        )
    return country.upper(), tags[country.upper()]


def shared_ideas(country):
    """Filter for countries with shared ideas"""
    msg = " shares HIE ideas with "
    if country in {"FLORENCE", "LAN"}:
        return "TUS", f"Florence{msg}Tuscany"
    elif country in {"CUSCO", "CSU"}:
        return ("INC", f"Cusco{msg}Inca")
    else:
        return False


class HIE(commands.Cog):
    """Historical Ideas Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Historical Ideas Expanded")
    async def hie(self, inter):
        pass

    @hie.sub_command(description="Steam Page")
    async def steam(self, inter):
        hie_embed = embed_maker.EmbedMaker(
            "Historical Ideas Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=2804377099",
            "The Best Ideas!",
            0xD5000,
            "Made by Melvasul and co.",
            "https://steamuserimages-a.akamaihd.net/ugc/1811020692174253502/E725A7D56284A2032F65453842F507B377F5D693/",
        )
        await inter.send(embed=hie_embed.embed)

    @hie.sub_command(description="Search for a Nation or its tag")
    async def find(self, inter, *, country_in: str = commands.Param(name="country")):
        with open("./data/HIE.json", "r", encoding="utf-8") as f:
            hie_data = json.load(f)
        with open("data/tags/tags.json", "r", encoding="utf-8") as f:
            tags = json.load(f)
        with open("data/tags/tagsHIE.json", "r", encoding="utf-8") as f:
            hie_tags = json.load(f)
        tags.update(hie_tags)

        country_lst = country_in.split(",")
        for country in country_lst:
            # Get rid of hanging whitespace
            country = country.strip()

            # Check if the country is a special HIE nation
            if tag := hie_special(country):
                tag, nation, prev_nation = tag
                message = ""
                for suffix in prev_nation:
                    form_nation = f"{nation}{suffix}"
                    next_idea = ideas_message("HIE", form_nation, hie_data)
                    if len(f"{message}{next_idea}") > 2000:
                        await inter.send(message)
                        message = ""
                    message += next_idea
                await inter.send(message)
                continue

            # Check ideas sharing countries
            elif message := shared_ideas(country.upper()):
                country, message = message
                await inter.send(message)

            # Check Hawaii
            elif country.title() in {"Hawai'i", "Hawaii"}:
                await inter.send("Vanilla EU4 has 2 Hawai'is. Please use their tags (UHW or HAW) instead.")
                continue

            # Check if country has special character(s)
            elif temp := accessory(country.title()):
                country = temp

            # Get country name and tag
            try:
                tag, nation = country_filter(country.title(), tags)
            except Exception:
                await inter.send(f"Is {country} Bielefeld? Pizza-chan is sure it doesn't exist. Report to Vielor or Melvasul otherwise.")
                continue

            try:
                message = ideas_message("HIE", nation, hie_data)
                await inter.send(message)
            except Exception:
                await inter.send(f"The country {nation} has no HIE ideas, for now...")

    @hie.sub_command(description="Shows a list of all special formables nations")
    async def formables(self, inter):
        with open("data/tags/tagsHIE.json", "r", encoding="utf-8") as f:
            tags = json.load(f)

        message = "```"
        for tag in tags:
            message += f"{str(tag)} : {str(tags[tag])} \n"
        await inter.send(f"{message}```")

    @hie.sub_command(description="Shows a list of all Countries in HIE")
    async def countries(self, inter):
        with open("./data/HIE.json", "r", encoding="utf-8") as f:
            hie_data = json.load(f)
        country_lst = sorted([key.title() for key in hie_data])

        message = "```"
        for country in country_lst:
            if len(f"{message}{country}\n```") > 2000:
                await inter.send(f"{message}```")
                message = "```"
            message += f"{country}\n"
        await inter.send(f"{message}```")

    @hie.sub_command(description="Show a picture of all nations with reworked ideas")
    async def map(self, inter):
        await inter.send(file=disnake.File(r"./data/images/hiemap.png"))
        await inter.followup.send(
            "The map does not include: Holy Roman Empire, Germany",
            file=disnake.File(r"./data/images/hiemapformables.png"),
        )


def setup(bot):
    bot.add_cog(HIE(bot))
