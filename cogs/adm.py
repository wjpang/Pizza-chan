import os

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()
EMF_SERVER_ID = os.getenv("EMF_SERVER_ID")
REACT_CHANNEL_ID = os.getenv("REACT_CHANNEL_ID")
REACT_MESSAGE_ID = os.getenv("REACT_MESSAGE_ID")
BOTCAVE_CHANNEL_ID = os.getenv("BOTCAVE_CHANNEL_ID")


class ADM(commands.Cog):
    """Botmakers functions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(case_insensitive=True, invoke_without_command=True)
    async def adm(self, ctx):
        """Greets the maker... or condemns the pretender"""
        if ctx.invoked_subcommand is None:
            author_roles = ctx.author.roles
            if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles):
                await ctx.send("Hello, my blessed masters!")

    @adm.command(pass_context=True)
    async def clean(self, ctx, *, amount: str):
        """Cleans the command message and the specified number of messages before it"""
        author_roles = ctx.author.roles
        if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles):
            await ctx.channel.purge(limit=int(amount) + 1)

    @adm.command(pass_context=True)
    async def players(self, bot, ctx):
        guild = bot.get_guild(EMF_SERVER_ID)
        player_role = disnake.utils.get(guild.roles, name="Player")
        channel = guild.get_channel(REACT_CHANNEL_ID)
        message = await channel.fetch_message(REACT_MESSAGE_ID)
        for reaction in message.reactions:
            if reaction.emoji.name != "thonk":
                continue
            async for user in reaction.users():
                if not isinstance(user, disnake.User) and player_role not in user.roles:
                    await bot.get_channel(BOTCAVE_CHANNEL_ID).send(f"User {user} reacted but did not receive the role")
                    await user.add_roles(player_role)


def setup(bot):
    bot.add_cog(ADM(bot))
