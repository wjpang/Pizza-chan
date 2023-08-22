import json

import disnake
from disnake.ext import commands

import embed_maker


def monument_filter(monument):
    """Fixes some case issues in monument names"""
    change_lst = {
        " Of ": " of ",
        " De ": " de ",
        " Al-": " al-",
        "-E ": "-e ",
        " Ve'": " ve'",
        " The ": " the ",
        " Op ": " op ",
        " Van ": " van ",
        "'S": "'s",
        " Di ": " di ",
        " Dei ": " dei ",
        "Ii": "II",
        " Della ": " della ",
        " La ": " la ",
        " Des ": " des ",
        " And ": " and ",
        " Da ": " da ",
    }
    for old, new in change_lst.items():
        monument = monument.replace(old, new)
    return monument


def accessory(monument):
    """Filter for monument names with special chars"""
    monument_dict = {
        "St. Patrick's Cathedral": [
            "St Patricks Cathedral",
            "St. Patricks Cathedral",
            "St Patrick's Cathedral",
        ],
        "Eszterháza": ["Eszterhaza"],
        "Református Nagytemplom": ["Reformatus Nagytemplom"],
        "Mont Saint-Michel": ["Mont Saint Michel", "Mont Saintmichel"],
        "Al-Qasr al-Muriq": [
            "Al-Qasr Al Muriq",
            "Al-Qasr Almuriq",
            "Al Qasr al-Muriq",
            "Al Qasr Al Muriq",
            "Al Qasr Almuriq",
            "Alqasr al-Muriq",
            "Alqasr Al Muriq",
            "Alqasr Almuriq",
        ],
        "Casa de Contratación": ["Casa de Contratacion"],
        "Mosque-Cathedral of Cordoba": [
            "Mosque Cathedral of Cordoba",
            "Mosquecathedral of Cordoba",
        ],
        "Università di Bologna": ["Universita di Bologna"],
        "Bishop's Palace": ["Bishops Palace"],
        "Sint-Pietersabdij": ["Sint Pietersabdij", "Sintpietersabdij"],
        "Al-Kadhimiya Mosque": ["Alkadhimiya Mosque", "Al Kadhimiya Mosque"],
        "Al-Madina Souq": ["Almadina Souq", "Al Madina Souq"],
        "Al-Mustansiriya": ["Almustansiriya", "Al Mustansiriya"],
        "Qasr al-Azm": ["Qasr Alazm", "Qasr Al Azm"],
        "Shaf ve'Yativ Synagogue": ["Shaf Veyativ Synagogue", "Shaf Ve Yativ Synagogue"],
        "Gonbad-e Qabus Tower": ["Gonbade Qabus Tower", "Gonbad E Qabus Tower"],
        "Sheikh Safi al-Din": ["Sheikh Safi Aldin", "Sheikh Safi Al Din"],
        "Shrine of Fatimah al-Masumeh": [
            "Shrine of Fatimah Almasumeh",
            "Shrine of Fatimah Al Masumeh",
        ],
        "College de Genève": ["College de Geneve"],
        "Schönbrunn Palace": ["Schonbrunn Palace"],
    }
    return next((key for key, value in monument_dict.items() if monument in value), monument)


color_map = {
    "Province": "\u001B[0;33m",  # Red
    "Starting Tier": "\u001B[0;33m",  # Green
    "Monument Trigger": "\u001B[0;33m",  # Blue
    "Tier 1": "\u001B[0;33m",
    "Tier 2": "\u001B[0;33m",
    "Tier 3": "\u001B[0;33m",
    "Province Modifiers": "\u001B[0;33m",
    "Area Modifier": "\u001B[0;33m",
    "Region Modifier": "\u001B[0;33m",
    "Country Modifiers": "\u001B[0;33m",
    "Conditional Modifier": "\u001B[0;33m",
    "Trigger": "\u001B[0;33m",
    "Modifier": "\u001B[0;33m",
}
pretty_lst = {
    "{": "[",
    "}": "]",
    ": \u001B[0;34mTrue\u001B[0;0m": "",
    "'": "",
    "[]": "\u001B[0;31mNone\u001B[0;0m",
}
stuff_to_color = [
    "Province",
    "Starting Tier",
    "Monument Trigger",
    "Tier 1",
    "Tier 2",
    "Tier 3",
    "Province Modifiers",
    "Area Modifier",
    "Region Modifier",
    "Country Modifiers",
    "Conditional Modifier",
    "Trigger",
    "Modifier",
]


class GME(commands.Cog):
    """Great Monuments Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Great Monuments Expanded")
    async def gme(self, inter):
        pass

    @gme.sub_command(description="Steam Page")
    async def steam(self, inter):
        gme_embed = embed_maker.EmbedMaker(
            "Great Monuments Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=2469419235",
            "We have Monuments!",
            0xD5000,
            "Made by Melvasul and co.",
            "https://steamuserimages-a.akamaihd.net/ugc/1768202791740244988/FE404404D83AB86A054F7BC66266B0C164D5020D/",
        )
        await inter.send(embed=gme_embed.embed)

    @gme.sub_command(description="Gives a link for even more monuments info")
    async def info(self, inter):
        gme_embed_info = embed_maker.EmbedMaker(
            "Great Monuments Expanded",
            "https://steamcommunity.com/workshop/filedetails/discussion/2469419235/3132793555948718378/",
            "Additional Information",
            0xFF2600,
            "List of all new Monuments",
            "https://steamuserimages-a.akamaihd.net/ugc/1768202791740244988/FE404404D83AB86A054F7BC66266B0C164D5020D/",
        )
        await inter.send(embed=gme_embed_info.embed)

    @gme.sub_command(description="Can search both a region or a monument")
    async def find(self, inter, *, monument_in: str = commands.Param(name="monument")):
        indent = 0
        chunk_size = 1995
        with open("./data/GME.json", "r", encoding="utf-8") as f:
            gme_data = json.load(f)
        regions_lst = sorted([key.title() for key in gme_data])

        monument_region_lst = monument_in.split(",")
        for monument_region in monument_region_lst:
            monument_region = monument_region.strip().title()
            if monument_region in regions_lst:
                try:
                    message = f"```ansi\n\u001B[0;33m{monument_region} Region Monuments\u001B[0;0m\n---------\n"
                    for monument in gme_data[monument_region]:
                        message += f"{monument}\n"
                    await inter.send(f"{message}```")
                except Exception:
                    await inter.send(f"The region: {monument_region} has no monuments from GME")
                continue
            else:
                # This will run if someone searches for a specific monument
                monument = accessory(monument_filter(monument_region))
                message = f"```ansi\n\u001B[0;33m{monument}\u001B[0;0m \n---------\n"
                found = 0
                for region, region_monuments in gme_data.items():
                    if monument not in region_monuments:
                        continue
                    found = 1
                    # message += build_message(gme_data[region][monument])
                    for stats, vals in gme_data[region][monument].items():
                        if isinstance(vals, dict):
                            message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m:\n"
                            message += build_message(vals, indent + 1, stuff_to_color)
                        elif stats in stuff_to_color:
                            color = color_map.get(stats, "")  # Get the color for the stat
                            message += "\t" * indent + f"{color}{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m\n"
                        else:
                            message += "\t" * indent + f"{stats}: \u001B[0;34m{vals}\u001B[0;0m \n"
                        for old, new in pretty_lst.items():
                            message = message.replace(old, new)
                    if len(f"{message}\n```") >= 2000:
                        chunks = [message[i : i + chunk_size] for i in range(0, len(message), chunk_size)]
                        for chunk in chunks:
                            if not chunk.startswith("```ansi"):
                                await inter.send(f"```ansi\n{chunk}```")
                            else:
                                await inter.send(f"{chunk}```")
                        message = "```\n"
                    else:
                        await inter.send(f"{message}```")
                    break
            if not found:
                await inter.send(f"The monument/region: {monument_region} does not exist in GME")

    @gme.sub_command(description="Show a map of all monuments in the world")
    async def map(self, inter):
        await inter.send(file=disnake.File(r"./data/images/gmemap.png"))

    @gme.sub_command(description="Show list of all Regions in GME")
    async def regions(self, inter):
        print("GME region list request received")
        with open("./data/GME.json", "r", encoding="utf-8") as f:
            gme_data = json.load(f)

        message = "```These are all the regions with GME monuments\n---------\n"
        regions_lst = sorted([key.title() for key in gme_data])
        for region in regions_lst:
            message += f"{region} \n"
        await inter.send(f"{message}```")


def setup(bot):
    bot.add_cog(GME(bot))


def build_message(data, indent=0, stuff_to_color=None):
    message = ""

    for stats, vals in data.items():
        if isinstance(vals, dict):
            message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m:\n"
            message += build_message(vals, indent + 1, stuff_to_color)
        elif stats in stuff_to_color:
            color = color_map.get(stats, "")
            message += "\t" * indent + f"{color}{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m\n"
        else:
            message += "\t" * indent + f"{stats}: \u001B[0;34m{vals}\u001B[0;0m \n"
    return message
