import os

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
        guild = self.bot.get_guild(EMF_SERVER_ID)
        player_role = disnake.utils.get(guild.roles, name="Player")
        channel = guild.get_channel(REACT_CHANNEL_ID)
        message = await channel.fetch_message(REACT_MESSAGE_ID)
        for reaction in message.reactions:
            if reaction.emoji.name != "thonk":
                continue
            async for user in reaction.users():
                if not isinstance(user, disnake.User) and player_role not in user.roles:
                    await self.bot.get_channel(BOTCAVE_CHANNEL_ID).send(f"User {user} reacted but did not receive the role")
                    await user.add_roles(player_role)

    @adm.command(pass_context=True)
    async def leave(self, ctx, *, guild_name):
        author_roles = ctx.author.roles
        if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles) or ctx.author.id == MELVA_ID:
            guild = disnake.utils.get(self.bot.guilds, name=guild_name)
            await guild.leave()


def setup(bot):
    bot.add_cog(ADM(bot))
