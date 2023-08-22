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


class VANILLA(commands.Cog):
    """Vanilla"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(case_insensitive=True, invoke_without_command=True)
    async def vanilla(self, inter):
        pass

    @vanilla.sub_command(description="Search for a Nation or its tag")
    async def ideas(self, inter, *, country_in: str = commands.Param(name="country")):
        with open("./data/00_vanilla_country_ideas.json", "r", encoding="utf-8") as f:
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
                vanilla_body_message = f"```Vanilla: {nation} Ideas \n---------\n"
                for key, values in vanilla_data[nation].items():
                    vanilla_body_message += f"{key.title()}: {values} \n"
                await inter.send(ftfy.fix_text(f"{vanilla_body_message}```"))
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
