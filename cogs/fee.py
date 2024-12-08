import json
import random

import disnake
from disnake.ext import commands

import embed_maker


def event_message(mod, nation, data):
    """Creates the event message block for nation in mod"""
    message = f"\n```{mod.upper()}: {nation} Events\n---------\n"
    for key, values in data[nation].items():
        message += f"{key.title()}: {values}\n"
    message += "```"
    return message


def event_filter(event):
    """Fixes some case issues in event names"""
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
        event = event.replace(old, new)
    return event


def accessory(event):
    """Filter for event names with special chars"""
    event_dict = {"Eszterháza": ["Eszterhaza"]}
    return next((key for key, value in event_dict.items() if event in value), event)


def country_filter(country, tags):
    """Filter for country names of length 3"""
    if country in {"Sus", "Chu", "Zia", "Lau", "Han", "Sui", "Wei", "Xia", "Rûm"} or len(country) != 3:
        return country
    return tags[country.upper()]


color_map = {
    "Province": "\u001B[0;33m",  # Red
    "Starting Tier": "\u001B[0;33m",  # Green
    "Monument Trigger": "\u001B[0;33m",  # Blue
    "Tier 1": "\u001B[0;33m",
    "Tier 2": "\u001B[0;33m",
    "Tier 3": "\u001B[0;33m",
    "Culture": "\u001B[0;33m",
    "Culture Group": "\u001B[0;33m",
    "Religion": "\u001B[0;33m",
    "Religion Group": "\u001B[0;33m",
    "Area": "\u001B[0;33m",
    "Is Year": "\u001B[0;33m",
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
    "Culture",
    "Culture Group",
    "Religion",
    "Religion Group",
    "Area",
    "Is Year",
]


class FEE(commands.Cog):
    """Flavour and Events Expanded"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Flavour and Events Expanded")
    async def fee(self, inter):
        pass

    @fee.sub_command(description="Steam Page")
    async def steam(self, inter):
        fee_embed = embed_maker.EmbedMaker(
            "Flavour and Events Expanded",
            "https://steamcommunity.com/sharedfiles/filedetails/?id=2185445645",
            "A little bit of Spice!",
            0xD5000,
            "Made by Uber & co.",
            "https://steamuserimages-a.akamaihd.net/ugc/1800901438645064071/46C48A835769FC3C38E8F74AA9C4F2D232B224A8/",
        )
        await inter.send(embed=fee_embed.embed)
        if random.randrange(1, 1001) >= 500:
            await inter.send_message(file=disnake.File(r"./files/hedgehog_avocado.png"))

    @fee.sub_command(description="You can search for disasters")
    async def disaster(self, inter, *, disaster_in: str = commands.Param(name="disaster")):
        indent = 0
        chunk_size = 1988

        with open("./data/Disaster.json", "r", encoding="utf-8") as f:
            fee_data = json.load(f)

        disaster_list = sorted([key.title() for key in fee_data])
        disaster_in_list = disaster_in.split(",")

        message = ""
        for disaster_in in disaster_in_list:
            disaster_in = disaster_in.strip().title()
            if disaster_in not in disaster_list:
                await inter.send(f"The disaster: {disaster_in} does not exist in FEE")
            else:
                message = f"```ansi\n\u001B[0;33m{disaster_in}\u001B[0;0m\n---------\n"
                for stats, vals in fee_data[disaster_in].items():
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
                    chunks = [message[i: i + chunk_size] for i in range(0, len(message), chunk_size)]
                    for chunk in chunks:
                        if not chunk.startswith("```ansi"):
                            await inter.send(f"```ansi\n{chunk}```")
                        else:
                            await inter.send(f"{chunk}```")
                    message = "```\n"
                else:
                    await inter.send(f"{message}```")

    @fee.sub_command(description="You can search events from the /fee events command")
    async def find(self, inter, *, event_in: str = commands.Param(name="nation")):
        indent = 0
        chunk_size = 1990

        with open("./data/FEE.json", "r", encoding="utf-8") as f:
            fee_data = json.load(f)
        with open("data/tags/tags.json", "r", encoding="utf-8") as f:
            tags = json.load(f)
        event_list = sorted([key.title() for key in fee_data])

        event_nation_lst = event_in.split(",")
        for event_nation in event_nation_lst:
            event_nation = event_nation.strip().title()
            if len(event_nation) == 3:
                # Get country name and tag
                try:
                    event_nation = country_filter(event_nation.title(), tags)
                except Exception:
                    await inter.send(f"Is {event_nation} Bielefeld? Pizza-chan is sure it doesn't exist. Report to Vielor or Melvasul otherwise.")
                    continue
            if event_nation in event_list:
                try:
                    message = f"```ansi\n\u001B[0;33m{event_nation} events\u001B[0;0m:\n---------\n"
                    for event in fee_data[event_nation]:
                        if len(f"{message}{event}\n```") > 2000:
                            await inter.send(f"{message}```")
                            message = "```"
                        message += f"{event}\n"
                    await inter.send(f"{message}```")
                except Exception:
                    await inter.send(f"{event_nation} has no events from FEE")
                continue
            # This will run if someone searches for a specific event
            event = accessory(event_filter(event_nation))
            found = 0
            for _, country_events in fee_data.items():
                eventstuff = {}
                for eventname, eventstuff in country_events.items():
                    if eventname.title() != event.title():
                        continue
                    found = 1
                    break
                if found != 1:
                    continue
                found = 1
                message = f"```ansi\n\u001B[0;33m{event}\u001B[0;0m:\n---------\n"
                for stats, vals in eventstuff.items():
                    if isinstance(vals, dict) and stats != "Hidden Effect":
                        message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m:\n"
                        message += build_message(vals, indent + 1, stuff_to_color)
                    else:
                        message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m \n"

                    for old, new in pretty_lst.items():
                        message = message.replace(old, new)

                    if len(f"{message}```") > 2000:
                        chunks = [message[i: i + chunk_size] for i in range(0, len(message), chunk_size)]
                        for chunk in chunks:
                            if not chunk.startswith("```ansi"):
                                await inter.send(f"```ansi\n{chunk}```")
                            else:
                                await inter.send(f"{chunk}```")
                        message = "```ansi\n"

                await inter.send(f"{message}```")
                break
            if not found:
                await inter.send(f"{event_nation} is not an event in FEE")

    @fee.sub_command(description="Shows a list of all Events in FEE")
    async def events(self, inter):
        with open("./data/FEE.json", "r", encoding="utf-8") as f:
            fee_data = json.load(f)

        message = "```These are all the countries with FEE events\n---------\n"
        event_list = sorted([key.title() for key in fee_data])
        for event in event_list:
            event = event.replace("Plc", "PLC")
            event = event.replace("Hre", "HRE")
            if len(f"{message}{event}\n```") > 2000:
                await inter.send(f"{message}```")
                message = "```"
            message += f"{event} \n"
        await inter.send(f"{message}```")

    @fee.sub_command(description="Shows a list of all disasters in FEE")
    async def disasters(self, inter):
        with open("./data/Disaster.json", "r", encoding="utf-8") as f:
            fee_data = json.load(f)

        message = "```These are all the disasters in FEE\n---------\n"
        disaster_list = sorted([key.title() for key in fee_data])

        for disaster in disaster_list:
            message += f"{disaster} \n"
        await inter.send(f"{message}```")

    # @fee.sub_command(description="Returns a map of all nations with FEE events")
    # async def map(self, inter):
    # """
    #     await inter.send(
    #         "https://cdn.discordapp.com/attachments/443910399599837189/739380589345505290/FEE_MAP.png?"
    #     )

    @fee.sub_command(description="Returns a wiki of all nations with FEE events")
    async def wiki(self, inter):
        await inter.send("https://eu4.paradoxwikis.com/Flavour_and_Events_Expanded")


def setup(bot):
    bot.add_cog(FEE(bot))


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
                    if stats == 'Custom Tooltip':
                        message += "\t" * indent + f"{item}\n".title()
                    else:
                        message += "\t" * indent + f"{stats}: {vals} \n".title()
                        break
        elif stats in stuff_to_color:
            color = color_map.get(stats, "")
            message += "\t" * indent + f"{color}{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m\n"
        else:
            message += "\t" * indent + f"{stats}: \u001B[0;34m{vals}\u001B[0;0m \n"

    return message
