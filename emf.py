# import json
import os
import sys

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.bans = True


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


# load cogs
bot = commands.Bot(command_prefix="+", intents=intents, description="A Pizza Pizza Bot", case_insensitive=True, reload=True, max_messages=1000000000)
bot.remove_command("help")
startup_extensions = [
    "cogs.events",
    "cogs.adm",
    "cogs.commands",
    "cogs.vanilla",
    "cogs.emf",
    "cogs.ase",
    "cogs.ate",
    "cogs.fee",
    "cogs.ge",
    "cogs.gme",
    "cogs.hree",
    "cogs.pte",
    "cogs.se",
    "cogs.tge",
    "cogs.hie",
    "cogs.viking",
]
for ext in startup_extensions:
    try:
        bot.load_extension(ext)
    except Exception as e:
        print(f"Something went wrong when loading extension {ext}: {e}")

# TODO: Save message cache periodically


def __init__(self, bot):
    self.bot = bot
    self.member = disnake.Member
    self.guild = disnake.guild


@bot.command()
@commands.has_role("Botmakers")
async def reload(ctx):
    """Reloads extensions"""
    await ctx.send("Reloading extensions...")
    for exten in startup_extensions:
        try:
            bot.reload_extension(exten)
        except Exception as err:
            await ctx.send(f"Something went wrong when loading extension {exten}: {err}")
    await ctx.send("Reloaded!")


@bot.command()
async def restart(ctx):
    """Saves the message cache and restarts the entire bot (message cache not implemented 100%)"""
    author_roles = ctx.author.roles
    if any(role.name in {"Botmakers", "Admin", "Moderators", "Staff", "Lead Devs"} for role in author_roles):
        # await ctx.send("Saving cache...")
        # with open("./pizza_cache/message_cache.json", "r", encoding="utf-8") as f:
        #     cache = json.load(f)
        # num_msg = len(bot.cached_messages)
        # await ctx.send(f"Messages to process: {num_msg}")
        # i = 0
        # temp = bot.cached_messages
        # while temp := list(bot.cached_messages)[i:]:
        #     try:
        #         msg = temp[0]
        #         if not msg.author.bot:
        #             message = await bot.get_channel(msg.channel.id).fetch_message(msg.id)
        #             cache[str(msg.id)] = {"content": message.content}
        #             if att := message.attachments:
        #                 cache[str(msg.id)]["attachments"] = att
        #             cache[str(msg.id)]["channel_id"] = msg.channel.id
        #             cache[str(msg.id)]["author_id"] = msg.author.id
        #             try:
        #                 cache[str(msg.id)]["channel_parent_id"] = msg.channel.parent.id
        #             except AttributeError:
        #                 i += 1
        #                 continue
        #         i += 1
        #     except Exception as error:
        #         print(error)
        #         i += 1
        # if i != len(bot.cached_messages):
        #     # This should never be reached, but I'm leaving it here in case
        #     await ctx.send(f"Process stopped as {i} saved messages does not match {len(bot.cached_messages)} total number of messages")
        #     return
        # with open("./pizza_cache/message_cache.json", "w", encoding="utf-8") as f:
        #     json.dump(cache, f, indent="\t", separators=(",", ": "), ensure_ascii=False) #) #, sort_keys=True)
        # await ctx.send("Cache saved!")
        await ctx.send("Restarting...")
        os.execv(sys.executable, ["python"] + sys.argv)


@bot.command()
@commands.has_role("Botmakers")
async def servers(ctx):
    """Get all servers the bot is in"""
    guild_lst = bot.guilds
    for guild in guild_lst:
        await ctx.send(guild)


print("Pizza Pizza Pii~")
bot.run(DISCORD_TOKEN, reconnect=True)
