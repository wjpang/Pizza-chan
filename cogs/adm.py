import asyncio
import os

import json
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()
EMF_SERVER_ID = int(os.getenv("EMF_SERVER_ID", "0"))
REACT_CHANNEL_ID = int(os.getenv("REACT_CHANNEL_ID", "0"))
REACT_MESSAGE_ID = int(os.getenv("REACT_MESSAGE_ID", "0"))
BOTCAVE_CHANNEL_ID = int(os.getenv("BOTCAVE_CHANNEL_ID", "0"))
MELVA_ID = int(os.getenv("MELVA_ID", "0"))


class ADM(commands.Cog):
    """Botmakers functions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(case_insensitive=True, invoke_without_command=True)
    async def adm(self, ctx):
        """Greets the maker... or condemns the pretender"""
        if ctx.invoked_subcommand is None:
            author_roles = ctx.author.roles
            if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles) or ctx.author.id == MELVA_ID:
                await ctx.send("Hello, my blessed masters!")

    @adm.command(pass_context=True)
    async def clean(self, ctx, *, amount: str):
        """Cleans the command message and the specified number of messages before it"""
        author_roles = ctx.author.roles
        if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles) or ctx.author.id == MELVA_ID:
            await ctx.channel.purge(limit=int(amount) + 1)

    @adm.command(pass_context=True)
    async def players(self, ctx):
        user_count = 0
        guild = ctx.guild
        player_role = disnake.utils.get(guild.roles, name="Player")

        if not player_role:
            await ctx.send("The 'Player' role was not found.")
            return

        channel = guild.get_channel(REACT_CHANNEL_ID)
        message = await channel.fetch_message(REACT_MESSAGE_ID)

        for reaction in message.reactions:
            if reaction.emoji.name != "thonk":
                continue

            async for user in reaction.users():
                if not isinstance(user, disnake.User) and player_role not in user.roles:
                    await ctx.send(f"{user} reacted but did not have the 'Player' role. Adding the role now.")
                    await user.add_roles(player_role)
                    user_count += 1

        if not user_count:
            await ctx.send("Every user already had the 'Player' role.")

    @adm.command(pass_context=True)
    async def leave(self, ctx, *, guild_name):
        author_roles = ctx.author.roles
        if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles) or ctx.author.id == MELVA_ID:
            guild = disnake.utils.get(self.bot.guilds, name=guild_name)
            await guild.leave()

    @adm.command(pass_context=True)
    async def membersEMF(self, ctx, *, guild_name):
        author_roles = ctx.author.roles
        if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles) or ctx.author.id == MELVA_ID:
            guild = disnake.utils.get(self.bot.guilds, name=guild_name)
            members = "\n-".join([member.name for member in guild.text_channels])
            await ctx.send(members)

    @adm.command(pass_context=True)
    async def reboot(self, ctx):
        if ctx.author.id == MELVA_ID:
            await ctx.send("Rebooting...")
            await asyncio.sleep(2)
            await ctx.send("System will reboot in 5 seconds.")
            await asyncio.sleep(5)
            root_password = "Melvasul-94"
            command = f"echo {root_password} | sudo -S shutdown -r now"

            os.system(command)

    @adm.command(pass_context=True)
    async def discussion(self, ctx):
        with open("./data/GME.json", "r", encoding="utf-8") as f:
            gme_data = json.load(f)

        message = ""
        regions_lst = sorted([key.title() for key in gme_data])
        for region in regions_lst:
            message += f"\n[b]{region}[/b]\n"
            for key in gme_data[region]:
                message += f"{key}\n"
            if len(message) >= 1800:
                await ctx.send(message)
                message = ""

        await ctx.send(message)


def setup(bot):
    bot.add_cog(ADM(bot))
