import random

import disnake
from disnake.ext import commands


class COMMANDS(commands.Cog):
    """A list of all non-mod commands"""

    def __init__(self, bot):
        self.bot = bot
        self.thonk_lst = [
            "<:CommunistThonk:998921439094779914>",
            "<:Flemishthonk:998921579130007563>",
            "<:Hyperthonkang:998921596267941948>",
            "<:assasinthink:998921423806529577>",
            "<:baguettethink:998921424645402655>",
            "<:christmasthonk:998921437530312705>",
            "<:crusaderthonk:998921441435197561>",
            "<:depressedthinking:998921444731916338>",
            "<:france:998921582091190302>",
            "<:guessillthonk:998921584930721832>",
            "<:gunthink:998921587443118180>",
            "<:happygun:998921589859024927>",
            "<:hyperthonkeyes:998921599807930388>",
            "<:knoht:998921669039099934>",
            "<:lemonthonk:998921670377082901>",
            "<a:mmh_knoht:998973386967486496>",
            "<:owothonk:998953211958399166>",
            "<:pepethonk:998953301108330616>",
            "<:piratethonk:998953307613700117>",
            "<:puke_thonk:998953317784883250>",
            "<a:rainbowthonk:999002943619600524>",
            "<:sadhappythonk:998954016102953070>",
            "<:thinkcookie:998954028446785627>",
            "<:thinkduel:1002357779111104532>",
            "<:thinko:998954030183235654>",
            "<:thinku:998954151092428860>",
            "<:thinkwot:998954152577204265>",
            "<:thonk:998954157748801548>",
            "<:thonkWHAT:999936488651370516>",
            "<:thonkang:998954159753658479>",
            "<:thonkangry:999936473157619832>",
            "<:thonkcloud:999936474554306590>",
            "<:thonkdead:999936476093616148>",
            "<:thonkdevil:999936477788115064>",
            "<:thonkeyes:999936479570710528>",
            "<:thonkhappy:999936481130991627>",
            "<a:thonkhmm:999002947864232038>",
            "<:thonkok:999936483580457041>",
            "<:thonkpizza:999936486109610004>",
            "<a:thonkspin:999002949990756403>",
            "<a:thonkspinH:999002952062730310>",
            "<a:thonksun:999002955019718736>",
            "<a:thonkvanish:999002958681342023>",
            "<:wearythonk:999936492493340703>",
        ]

    @commands.slash_command(description="How many in this lovely server?")
    async def members(self, inter):
        total_members = inter.guild.member_count
        await inter.send(f"Our server has {total_members} professional map watchers!")

    @commands.slash_command(description="Member has bug... again")
    async def bug(self, inter):
        """Asks a bug reporter for a list of their mods"""
        await inter.send("Please provide a complete list of mods you are using.\nE.g. A screenshot of your playset from your launcher.")

    @commands.slash_command(description="Ban it")
    async def ban(self, inter):
        if random.choice([0, 1]):
            await inter.send("<:banhammer:998921426390220850> " * 3)
        else:
            await inter.send(file=disnake.File(r"./data/misc/ban.png"))

    @commands.slash_command(description="Buff it")
    async def buff(self, inter):
        if random.choice([0, 1]):
            await inter.send("<:buff:998921432161583115> " * 3)
        else:
            await inter.send(file=disnake.File(r"./data/misc/buff.png"))

    @commands.slash_command(description="Nerf it")
    async def nerf(self, inter):
        if random.choice([0, 1]):
            await inter.send("<:nerfhammer:998953205566292031> " * 3)
        else:
            await inter.send(file=disnake.File(r"./data/misc/nerf.png"))

    @commands.slash_command(description="ThinkDuel")
    async def duel(self, inter):
        if random.choice([0, 1]):
            await inter.send("<:thinkduel:1002357779111104532> " * 3)
        else:
            await inter.send(file=disnake.File(r"./data/misc/thinkduel.png"))

    @commands.slash_command(description="FAQ")
    async def faq(self, inter):
        await inter.send(file=disnake.File(r"./data/misc/faq.png"))

    @commands.slash_command(description="Chu Ko Noob")
    async def chu(self, inter):
        await inter.send(file=disnake.File(r"./data/misc/melva.png"))

    @commands.slash_command(description="Soviet Union")
    async def com(self, inter):
        await inter.send("https://tenor.com/view/iserve-soviet-union-chernobyl-handshake-gif-14664891")

    @commands.slash_command(description="Blessed be Ele")
    async def ele(self, inter):
        await inter.send("Blessed be thine kind")

    @commands.slash_command(description="Bonk Flem")
    async def flem(self, inter):
        await inter.send("Stop being horny, Flem " "<a:bonk:998973168272285696> " "<a:bonk:998973168272285696> " "<a:bonk:998973168272285696> ")

    @commands.slash_command(description="Praises Jay")
    async def jay(self, inter):
        await inter.send("Will Jay ever mod again?")

    @commands.slash_command(description="Lim?")
    async def lim(self, inter):
        await inter.send(file=disnake.File(r"./data/misc/lemon.jpg"))

    @commands.slash_command(description="Help Melva")
    async def melva(self, inter):
        await inter.send(
            "Give Melva a pizza or a hug, he needs it",
            file=disnake.File(r"./data/misc/chu.png"),
        )

    # @commands.slash_command(description="")
    # async def pascal(self, inter):
    #     """Pascal"""
    #         await inter.send(
    #             "When Papal ideas and tree Pascal? When Andalusian tree? Where Faction Rework?"
    #         )

    @commands.slash_command(description="Shiro")
    async def shiro(self, inter):
        await inter.send("Where Irish flavour?")

    @commands.slash_command(description="Vielor")
    async def vielor(self, inter):
        await inter.send("When will you work on me? <:pepe_hands:998953284104622130>")

    @commands.slash_command(description="Flavour")
    async def zach(self, inter):
        await inter.send(
            "Why did you took so much to update Zach?",
            file=disnake.File(r"./data/misc/zach.png"),
        )
        if random.choice([0, 1]):
            await inter.followup.send(file=disnake.File(r"./data/misc/hedgehog_avocado.png"))

    # @commands.slash_command(description="")
    # async def wiki(self, inter):
    #     """Link of the Expanded Mod Family"""
    #     await inter.send(
    #         "Here is the Expanded Family wiki:\n"
    #         "https://sites.google.com/view/missions-expanded-trees/home"
    #     )

    @commands.slash_command(description="Blame a person")
    async def blame(self, inter, *, person: str):
        # Create a string of 10 emojis randomly selected from ree and aaaaa
        scream_lst = ["<a:aaaaa:998973152526860398>", "<a:ree:999002945293127731>"]
        message = "".join(f"{random.choice(scream_lst)} " for _ in range(10))
        vowels = ["a", "e", "i", "o", "u", "y"]
        for i in range(-1, -len(person) - 1, -1):
            if person[i] in vowels:
                await inter.send(f"{person[:i]}{person[i] * 24}{person[i:]}".upper())
                break
            if i == -len(person):
                await inter.send(f"{person}{person[-1] * 24}".upper())
                break
        await inter.followup.send(message)

    @commands.slash_command(description="SCREAMMMM!!!!!!!!!!!!!!!!")
    async def scream(self, inter):
        scream_lst = ["<a:aaaaa:998973152526860398>", "<a:ree:999002945293127731>"]
        message = "".join(f"{random.choice(scream_lst)} " for _ in range(10))
        await inter.send(message)

    @commands.slash_command(description="EVEN MORE SCREAMMMM!!!!!!!!!!!!!!!!")
    async def screams(self, inter):
        scream_lst = ["<a:aaaaa:998973152526860398>", "<a:ree:999002945293127731>"]
        for _ in range(5):
            message = "".join(f"{random.choice(scream_lst)} " for _ in range(10)) + "\n"
            for _ in range(10):
                message += f"{random.choice(scream_lst)} "
            await inter.send(message)

    @commands.slash_command(description="DO NOT DEFY THE THONK!!!!!!!!!!!!!!!!")
    async def thonk(self, inter):
        thonk = "".join(f"{random.choice(self.thonk_lst)} " for _ in range(10))
        await inter.send(thonk)

    @commands.slash_command(description="EMF modlist that nobody seems to know")
    async def notemf(self, inter):
        await inter.send(
            "EMF only includes these mods:\nAny other Expanded mod that is not on the list is not part of the EMF",
            file=disnake.File(r"./data/images/EMF-mods.png"),
        )
        # await inter.followup.send("Any other Expanded mod that is not on the list above is not part of the EMF")


def setup(bot):
    bot.add_cog(COMMANDS(bot))
