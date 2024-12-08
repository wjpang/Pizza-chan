import json

import ftfy
from disnake.ext import commands


def shared_ideas(country):
    """Filter for countries with shared ideas"""
    msg = " shares vanilla ideas with "
    match country:
        # Netherlands ideas -> NED/HOL
        case "HOLLAND" | "HOL":
            return "NED", f"Holland{msg}Netherlands"
        # Austria ideas -> HAB/STY
        case "STYRIA" | "STY":
            return "HAB", f"Styria{msg}Austria"
        # Sicily ideas -> SIC/TTS
        case "TWO SICILIES" | "TTS":
            return "SIC", f"Two Sicilies{msg}Sicily"
        # Jianzhou ideas -> MJZ/MHX/NHX/MYR/EJZ
        case "HAIXI" | "UDEGE" | "YEREN" | "DONGHAI" | "MHX" | "NHX" | "MYR" | "EJZ":
            if country in {"MHX", "NHX", "MYR", "EJZ"}:
                country = {
                    "MHX": "Haixi",
                    "NHX": "Udege",
                    "MYR": "Yeren",
                    "EJZ": "Donghai",
                }[country]
            return country, f"{country.title()}{msg}Jianzhou"
        # Marathas ideas -> MAR/BDA/GWA
        case "BARODA" | "GWALIOR" | "BDA" | "GWA":
            if country in {"BDA", "GWA"}:
                country = {
                    "BDA": "Baroda",
                    "GWA": "Gwalior",
                }[country]
            return "MAR", f"{country.title()}{msg}Marathas"
        # Taungu ideas -> TAU/BPR
        case "PROME" | "BPR":
            return "TAU", f"Prome{msg}Taungu"
        # Tuscany ideas -> TUS/LAN
        case "FLORENCE" | "LAN":
            return "TUS", f"Florence{msg}Tuscany"
        # Hejaz ideas -> HED/MDA
        case "MEDINA" | "MDA":
            return "HED", f"Medina{msg}Hejaz"
        # Kongo ideas -> KON/LOA/NDO
        case "LOANGO" | "NDONGO" | "LOA" | "NDO":
            if country in {"LOA", "NDO"}:
                country = {
                    "LOA": "Loango",
                    "NDO": "Ndongo",
                }[country]
            return "KON", f"{country.title()}{msg}Kongo"
        # Pueblo ideas -> PUE/KER/ZNI
        case "ZIA" | "ZUNI" | "KER" | "ZNI":
            if country in {"KER", "ZNI"}:
                country = {
                    "KER": "Keres",
                    "ZNI": "Zuni",
                }[country]
            return "PUE", f"{country.title()}{msg}Pueblo"
        # Georgia ideas -> GEO/IME
        case "IMERETI" | "IME":
            return "GEO", f"Imereti{msg}Georgia"
        # Silesia ideas -> SIL/GLG/OPL
        case "GLOGOW" | "OPOLE" | "GLG" | "OPL":
            if country in {"GLG", "OPL"}:
                country = {
                    "GLG": "Glogow",
                    "OPL": "Opole",
                }[country]
            return "SIL", f"{country.title()}{msg}Silesia"
        # Inca ideas -> INC/CSU
        case "CUSCO" | "CSU":
            return "INC", f"Cusco{msg}Inca"
        # Armenia ideas -> ARM/MLK
        case "KHARAB" | "MLK":
            return "ARM", f"Kharab{msg}Armenia"
        # Katsina ideas -> KTS/KAN/ZZZ/HAU
        case "KANO" | "ZAZZAU" | "HAUSA" | "KAN" | "ZZZ" | "HAU":
            if country in {"KAN", "ZZZ", "HAU"}:
                country = {
                    "KAN": "Kano",
                    "ZZZ": "Zazzau",
                    "HAU": "Hausa",
                }[country]
            return "KTS", f"{country.title()}{msg}Katsina"
        # Kotte ideas -> CEY/KND
        case "KANDY" | "KND":
            return "CEY", f"Kandy{msg}Kotte"
        # Bremen ideas -> BRE/VER
        case "VERDEN" | "VER":
            return "BRE", f"Verden{msg}Bremen"
        # Catalonia ideas -> CAT/VAL/MJO
        case "VALENCIA" | "MAJORCA" | "VAL" | "MJO":
            if country in {"VAL", "MJO"}:
                country = {
                    "VAL": "Valencia",
                    "MJO": "Majorca",
                }[country]
            return "CAT", f"{country.title()}{msg}Catalonia"
        # Butua ideas -> RZW/RZI
        case "ROZWI EMPIRE" | "RZI":
            return "RZW", f"Rozwi Empire{msg}Butua"
        # Lüneburg ideas -> LUN/CLB
        case "CALENBERG" | "CLB":
            return "LUN", f"Calenberg{msg}Lüneburg"
        # Yemen ideas -> YEM/ADE
        case "ADEN" | "ADE":
            return "YEM", f"Aden{msg}Yemen"
        # Oirat ideas -> OIR/ZUN
        case "DZUNGAR" | "ZUN":
            return "OIR", f"Dzungar{msg}Oirat"
        # Dai Viet ideas -> DAI/TOK/ANN
        case "TONKIN" | "ANAM" | "TOK" | "ANN":
            if country in {"TOK", "ANN"}:
                country = {
                    "TOK": "Tonkin",
                    "ANN": "Anam",
                }[country]
            return "DAI", f"{country.title()}{msg}Dai Viet"
        # Aceh ideas -> ATJ/PSA
        case "PASAI" | "PSA":
            return "ATJ", f"Pasai{msg}Aceh"
        case _:
            return False


def accessory(country):
    """Fixes nation names with special chars"""
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
    "Province Modifiers": "\u001B[0;33m",
    "Area Modifier": "\u001B[0;33m",
    "Region Modifier": "\u001B[0;33m",
    "Country Modifiers": "\u001B[0;33m",
    "Conditional Modifier": "\u001B[0;33m",
    "Trigger": "\u001B[0;33m",
    "Modifier": "\u001B[0;33m",
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
    "[]": "",
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
    "Culture",
    "Culture Group",
    "Religion",
    "Religion Group",
    "Area",
    "Is Year",
]

def ideas_message(mod, nation, data):
    """Creates the ideas message block for nation in mod"""
    message = f"```ansi\n\u001B[0;33m{nation} Ideas\u001B[0;0m \n---------"
    for key, values in data[nation].items():
        if isinstance(values, dict):
            message += f"\n\u001B[0;33m{key.title()}\u001B[0;0m: "
            message += "{ "
            for k, v in values.items():
                if isinstance(v, dict):
                    message += "} "
                    message += f"\u001B[0;33m{k.title()}\u001B[0;0m: "
                    message += "{ "
                    for k_sub, v_sub in v.items():
                        message += f"{k_sub.title()}: \u001B[0;34m{v_sub}\u001B[0;0m, "
                else:
                    message += f"{k.title()}: \u001B[0;34m{v}\u001B[0;0m, "
            message += "}"
        else:
            message += f"\n{key.title()}: \u001B[0;34m{values}\u001B[0;0m"
    pretty_lst = {
        ", }": " }",
    }
    for old, new in pretty_lst.items():
        message = message.replace(old, new)
    return f"{message}```"


class VANILLA(commands.Cog):
    """Vanilla"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Vanilla")
    async def vanilla(self, inter):
        pass

    @vanilla.sub_command(description="Search for a Nation or its tag")
    async def ideas(self, inter, *, country_in: str = commands.Param(name="country")):
        with open("./data/Vanilla_ideas.json", "r", encoding="utf-8") as f:
            vanilla_data = json.load(f)
        with open("data/tags/tags.json", "r", encoding="utf-8") as f:
            tags = json.load(f)

        country_lst = country_in.split(",")
        for country in country_lst:
            country = country.strip()

            # Check ideas sharing countries
            if message := shared_ideas(country.upper()):
                country, message = message
                await inter.send(message)

            # Check Hawaii
            if country.title() in {"Hawai'i", "Hawaii"}:
                await inter.send("Vanilla EU4 has 2 Hawai'is. Please use their tags (UHW or HAW) instead.")
                continue

            # Check if country has special character(s)
            if temp := accessory(country.title()):
                country = temp

            # Get country name and tag
            try:
                nation = country_filter(country.title(), tags)
            except Exception:
                await inter.send(f"Is {country} Bielefeld? Pizza-chan is sure it doesn't exist. Report to Vielor or Melvasul otherwise.")
                continue

            try:
                message = ideas_message("", nation, vanilla_data)
                await inter.send(message)
            except Exception:
                await inter.send(f"{nation} either isn't a vanilla country or has generic ideas <:thinku:998954151092428860>\nIf you think this is a mistake, ping Melvasul or Vielor")

    @vanilla.sub_command(description="Turns a tag in a country")
    async def country(self, inter, *, tags_in: str = commands.Param(name="tag")):
        with open("data/tags/tags.json", "r", encoding="utf-8") as f:
            tags = json.load(f)
        tags_lst = tags_in.split(",")

        message = ""
        for tag in tags_lst:
            tag = tag.strip().upper()
            try:
                country = tags[tag]
                message += f"{country}\n"
            except Exception:
                message += f"{tag} doesn't exist oAo. If Pizza-chan is wrong, ping Melvasul or Vielor\n"
        await inter.send(ftfy.fix_text(message))

    @vanilla.sub_command(description="search for either reforms, tiers or governments")
    async def reform(self, inter, *, reform_in: str = commands.Param(name="reform")):
        indent = 0
        found = 0

        with open("./data/Vanilla_reforms.json", "r", encoding="utf-8") as f:
            vanilla_data = json.load(f)
        government_lst = sorted(vanilla_data.keys())

        reform_list = reform_in.split(",")

        for reform in reform_list:
            found = 0
            reform = reform.strip().title()
            if reform in government_lst:  # used to search for Monarchy, Republic, etc
                message = f"```ansi\n\u001B[0;33m{reform}:\u001B[0;0m\n---------\n"
                for government in vanilla_data[reform]:
                    message += f"{government}\n"
                await inter.send(f"{message}```")
                continue
            else:
                for government in government_lst:  # used to search specific tiers
                    if found == 1:
                        break
                    tier_lst = sorted(vanilla_data[government].keys())
                    if reform in tier_lst:
                        found = 1
                        message = f"```ansi\n\u001B[0;33m{reform}:\u001B[0;0m\n---------\n"
                        for tier in sorted(vanilla_data[government][reform].keys()):
                            message += f"{tier}\n"
                        await inter.send(f"{message}```")
                        break
                    else:
                        for tier in tier_lst:
                            reform_lst = sorted(vanilla_data[government][tier].keys())
                            if reform in reform_lst:
                                found = 1
                                message = f"```ansi\n\u001B[0;33m{reform}:\u001B[0;0m\n---------\n"
                                for stats, vals in vanilla_data[government][tier][reform].items():
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
                await inter.send(f"The searched government/tier/reform: {reform} does not exist")

    @vanilla.sub_command(description="You can search for a monument")
    async def monument(self, inter, *, monument_input: str = commands.Param(name="monument")):
        indent = 0
        chunk_size = 1988

        with open("./data/Vanilla_monuments.json", "r", encoding="utf-8") as f:
            monument_data = json.load(f)

        mon_input_list = monument_input.split(",")

        message = ""
        for monument_input in mon_input_list:
            monument_input = monument_input.strip().title()
            if monument_input not in monument_data:
                await inter.send(f"The Monument: {monument_input} does not exist in Vanilla")
            else:
                message = f"```ansi\n\u001B[0;33m{monument_input}\u001B[0;0m\n---------\n"
                for stats, vals in monument_data[monument_input].items():
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

    @vanilla.sub_command(description="Show all the monuments in Vanilla")
    async def monumentslist(self, inter):
        with open("./data/Vanilla_monuments.json", "r", encoding="utf-8") as f:
            monument_data = json.load(f)
        message = "```These are all the Monuments in Vanilla\n---------\n"
        monument_list = sorted([key.title() for key in monument_data])

        for monument in monument_list:
            message += f"{monument} \n"

        if len(f"{message}```") > 2000:
            chunk_size = 1990

            chunks = [message[i : i + chunk_size] for i in range(0, len(message), chunk_size)]
            for chunk in chunks:
                if not chunk.startswith("```"):
                    await inter.send(f"```{chunk}```")
                else:
                    await inter.send(f"{chunk}```")
            message = "```"

    @vanilla.sub_command(description="Turns a country in a tag")
    async def tag(self, inter, *, nations_in: str = commands.Param(name="country")):
        with open("data/tags/tags.json", "r", encoding="utf-8") as f:
            tags = json.load(f)
        nations = nations_in.split(",")

        message = ""
        for nation in nations:
            nation = nation.strip().title()
            if nation in {"Hawai'i", "Hawaii"}:
                message += "Vanilla EU4 has 2 Hawai'is. Please use their tags (UHW or HAW) instead.\n"
                continue
            elif temp := accessory(nation.title()):
                nation = temp
            try:
                tag = list(tags.keys())[list(tags.values()).index(nation)]
                message += f"{tag}\n"
            except Exception:
                message += f"{nation} doesn't exist oAo. If Pizza-chan is wrong, ping Melvasul or Vielor\n"
        await inter.send(ftfy.fix_text(message))


def setup(bot):
    bot.add_cog(VANILLA(bot))


def build_message(data, indent=0, stuff_to_color=None):
    message = ""

    for stats, vals in data.items():
        if isinstance(vals, dict):
            message += "\t" * indent + f"\u001B[0;33m{stats}\u001B[0;0m:\n"
            message += build_message(vals, indent + 1, stuff_to_color)
        elif isinstance(vals, list):
            message += "\t" * indent + f"\u001B[0;33m{stats.title()}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m\n"
            continue
            if len(vals) == 0:
                continue
            for item in vals:
                print(type(item), item)
                if isinstance(item, dict):
                    message += "\t" * indent + f"{stats}:\n".title()
                    message += build_message(item, indent + 1, stuff_to_color)
                elif isinstance(item, str):
                    message += "\t" * indent + f"{stats}: {vals} \n".title()
        elif stats in stuff_to_color:
            color = color_map.get(stats, "")
            message += "\t" * indent + f"{color}{stats}\u001B[0;0m: \u001B[0;34m{vals}\u001B[0;0m\n"
        else:
            message += "\t" * indent + f"{stats}: \u001B[0;34m{vals}\u001B[0;0m \n"
    return message
