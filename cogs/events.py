import datetime
import io
import os
import random
from pathlib import Path

import disnake
from dateutil import relativedelta
from disnake.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter, ImageFont

load_dotenv()
EMF_SERVER_ID = int(os.getenv("EMF_SERVER_ID"))
REACT_MESSAGE_ID = int(os.getenv("REACT_MESSAGE_ID"))
ACTION_LOG_CHANNEL_ID = int(os.getenv("ACTION_LOG_CHANNEL_ID"))
MULTIPLAYER_MESSAGE_ID = int(os.getenv("MULTIPLAYER_MESSAGE_ID"))
POLITICS_MESSAGE_ID = int(os.getenv("POLITICS_MESSAGE_ID"))

intents = disnake.Intents.default()
intents.members = True


background_folder = Path("./data/misc")
background_files = list(background_folder.glob("background*.png"))


class Events(commands.Cog):
    """Events"""

    def __init__(self, bot):
        self.bot = bot
        self.member = disnake.Member
        self.guild = disnake.guild
        self.welcome_message = [
            "Military Master? Diplomatic Devil? Administrative Assistant? No! He's none other than {}",
            "{} has a vision that spans far and wide, but since this is a 2D game, he can only view widely",
            "Legends say that {} has a father that smells of elder berries",
            "{} is a member of The Catholic League!",
            "{} is the leader of The Protestant League!",
            "Reformed Refugee: {} has joined our court",
            "Not all members of the Ulema are great theologians or intellectuals, just like {}",
            "Some of the more powerful monasteries have openly come out in support of {}",
            "{} has always succeeded above others at capturing Shiva's glory in art, ",
            "{}'s disciples are known as Sikhs and are spreading this new faith rapidly",
            "{} has had a lavish Bar Mitzvah!",
            "Rekindle the fire, {} is here!",
            "You're finally awake {}. You were trying to join the Holy Roman Empire. Walked right into that French ambush",
            "The throne of {} has just married into our dynasty. Take that von Habsburgs!",
            "{} has joined the trade league. Such is life.",
            "Welcome to the rice fields {}",
            "Discovery Spread: we now know of {}",
        ]
        self.goodbye_message = [
            "{} died in a hunting accident",
            "{} left with the Margherita takeaway",
            "A comet fell on {}'s head, -3 stab",
            "Looks like 0/0/0 {} was disinherited!",
            "{} has died, therefore their faction has been disbanded",
            "{} has been lost to a mysterious illness",
            "The traitor, {}, has been executed!",
            "{} just left. Well... they were Sus anyways",
            "{} shatt themselves. Lolland!",
            "{} was lost in a vessel while exploring the sea",
            "{} drank too much Rûm",
            "{}, fucking idiot leaving the server",
            "The rebel {} has risen up in our capital!",
            "{} was burnt at the stake like the witch they were",
            "My King, the rotten swine {} has declared war upon us! Prepare for battle!",
        ]
        self.role_message_id = REACT_MESSAGE_ID  # ID of message to react to for role
        self.emoji_to_role = {
            disnake.PartialEmoji(name="thonk", id=998954157748801548): 914106554876309544,  # ID of the role associated with a partial emoji's ID
        }

    async def create_welcome_image(self, member):
        def yeet(
            back_img,
            pfp,
            x_offset: int,
            y_offset: int,
            from_center: bool,
            font_size: int,
            msg: str,
            fill,
        ):
            fn = ImageFont.truetype("./data/misc/ANIRONBOLD.ttf", size=font_size)
            if from_center:
                text_width, _ = draw.textsize(msg, fn)
                pos = (back_img.size[0] - text_width) // 2
            else:
                pos = 0

            y0 = round((bg.size[-1] / 2) - (pfp.size[-1] / 2))

            # Bold shadow behind text
            txt_draw = ImageDraw.Draw(back_img)

            # Plain text
            txt_draw.multiline_text((pos + x_offset, y0 + 110 + y_offset), text=msg, font=fn, align="left", fill=fill)
            return back_img

        asset = member.display_avatar
        pfp_raw = await asset.read()
        pfp_img = Image.open(io.BytesIO(pfp_raw)).convert("RGBA")
        random_bg_path = random.choice(background_files)
        bg_raw = Image.open(random_bg_path).convert("RGBA")

        bg_png = bg_raw.copy()
        pfp_png = pfp_img.copy()
        bg = bg_png.resize((1650, 710))
        pfp = pfp_png.resize((256, 256))

        # Creates mask to make image a circle
        mask_im = Image.new("L", pfp.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse([0, 0, pfp.size[0], pfp.size[-1]], fill=255)

        # Pastes pfp onto background
        back_im = bg.copy()
        back_im = back_im.filter(ImageFilter.BLUR)
        back_im.paste(pfp, (675, 115), mask_im)

        # Draw gradient circle
        c = Image.new("RGBA", bg.size, color=(255, 255, 255, 1))
        draw = ImageDraw.Draw(c)
        r = 40
        z = 10
        for i in range(z):
            draw.ellipse(
                xy=[675 - z, 115 - z, pfp.size[0] + 675 + z, 115 + pfp.size[-1] + z],
                fill=None,
                outline=(0, 0, 0, 230 - r),
                width=z + 1 - i,
            )
            r += 20

        # Write stuff
        m1 = f"{member.display_name} has joined the server"
        m2 = f"Member #{member.guild.member_count}!"

        # msg1
        back_im = yeet(
            back_img=back_im,
            pfp=pfp,
            y_offset=35,
            x_offset=0,
            from_center=True,
            font_size=60,
            msg=m1,
            fill=(255, 255, 255),
        )

        # msg2
        back_im = yeet(
            back_img=back_im,
            pfp=pfp,
            y_offset=135,
            x_offset=0,
            from_center=True,
            font_size=60,
            msg=m2,
            fill=(255, 255, 255),
        )

        out = Image.alpha_composite(back_im, c)
        fp = io.BytesIO()
        out.save(fp, "png")
        fp.seek(0)
        return fp

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """member joining"""
        channel = member.guild.system_channel
        if channel.name == "new-peeps":
            image_welcome = await self.create_welcome_image(member)
            await channel.send(
                random.choice(self.welcome_message).format(str(member.mention)),
                file=disnake.File(image_welcome, filename=f"{member}WelcomeImage.png"),
            )
        if member.guild.id != EMF_SERVER_ID:
            return
        url = member.avatar.url if member.avatar is not None else member.default_avatar.url
        age = relativedelta.relativedelta(datetime.datetime.now(datetime.timezone.utc), member.created_at)
        year, month, day, hour, minute, second = (
            age.years,
            age.months,
            age.days,
            age.hours,
            age.minutes,
            age.seconds,
        )
        week = day // 7
        year_ln = f"{year} years, " if year > 1 else f"{year} year, "
        month_ln = f"{month} months, " if month > 1 else f"{month} month, "
        week_ln = f"{week} weeks, " if week > 1 else f"{week} week, "
        hour_ln = f"{hour} hrs, " if hour > 1 else f"{hour} hr, "
        minute_ln = f"{minute} mins, " if minute > 1 else f"{minute} min, "
        second_ln = f"{second} secs" if second > 1 else f"{second} sec"
        if month >= 1 or year >= 1:
            day_ln = f"{day} days" if day > 1 else f"{day} day"
            age_ln = f"{year_ln}{month_ln}{day_ln}" if year >= 1 else f"{month_ln}{day_ln}"
        else:
            day = day % 7
            day_ln = f"{day} days, " if day > 1 else f"{day} day, "
            if week > 0:
                age_ln = f"{week_ln}{day_ln}{hour_ln}{minute_ln}{second_ln}"
            elif day > 0:
                age_ln = f"{day_ln}{hour_ln}{minute_ln}{second_ln}"
            elif hour > 0:
                age_ln = f"{hour_ln}{minute_ln}{second_ln}"
            elif minute > 0:
                age_ln = f"{minute_ln}{second_ln}"
            else:
                age_ln = f"{second_ln}"
        await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
            embed=(
                disnake.Embed(
                    description=f"{member.mention} {member.name}#{member.discriminator}",
                    color=0x43B582,
                    timestamp=datetime.datetime.now(),
                )
                .set_author(
                    name="Member Joined",
                    icon_url=url,
                )
                .set_thumbnail(
                    url=url,
                )
                .add_field(
                    name="**Account Age**",
                    value=f"{age_ln}",
                    inline=False,
                )
                .set_footer(text=f"ID: {member.id}")
            )
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """member leaving"""
        channel = member.guild.system_channel
        if channel.name == "new-peeps":
            await channel.send(random.choice(self.goodbye_message).format(str(member.mention)))
        if member.guild.id != EMF_SERVER_ID:
            return
        url = member.avatar.url if member.avatar is not None else member.default_avatar.url
        tri_nl = "" if member.roles[1:] else "\n\n\n"
        embed = (
            disnake.Embed(
                description=f"{member.mention} {member.name}#{member.discriminator}{tri_nl}",
                color=0xFF470F,
                timestamp=datetime.datetime.now(),
            )
            .set_author(
                name="Member Left",
                icon_url=url,
            )
            .set_thumbnail(
                url=url,
            )
            .set_footer(text=f"ID: {member.id}")
        )
        if member.roles[1:]:
            embed = embed.add_field(
                name="**Roles**",
                value=" ".join([f"{role.mention}" for role in member.roles[1:]]),
                inline=False,
            )
        await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ignores random '+' signs that could be misinterpreted as commands"""
        if isinstance(error, commands.CommandNotFound):
            # Changed to a print in case any errors that we might have gotten can be gotten
            print(error)

    @commands.Cog.listener()
    async def on_message(self, message):
        """random pings"""
        if message.author == self.bot.user:
            return
        content = message.content
        if content.lower() in {"ping", "pong"}:
            await message.channel.send("https://tenor.com/view/cat-ping-pong-funny-animals-cats-gif-8766860")
        elif content.lower() == "wake":
            await message.channel.send("https://tenor.com/view/naudiyal-shubidubi-pingu-wakeup-wake-up-gif-17260204")
        elif content == "/o/":
            await message.channel.send("\\o\\")
        elif content == "\\o\\":
            await message.channel.send("/o/")
        elif content in {"o/", "\\o", "o7"}:
            await message.channel.send("Salutations o7")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Player auto-role reaction add"""
        message_id = payload.message_id
        if message_id == REACT_MESSAGE_ID:
            guild_id = payload.guild_id
            guild = disnake.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            if payload.emoji.name == "thonk":
                role = disnake.utils.get(guild.roles, name="Player")

            member = disnake.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.add_roles(role)
        elif message_id == MULTIPLAYER_MESSAGE_ID:
            guild_id = payload.guild_id
            guild = disnake.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            if payload.emoji.name == "florrypog":
                role = disnake.utils.get(guild.roles, name="MP Member")

            member = disnake.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.add_roles(role)
        elif message_id == POLITICS_MESSAGE_ID:
            guild_id = payload.guild_id
            guild = disnake.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            if payload.emoji.name == "there_was_no_meme":
                role = disnake.utils.get(guild.roles, name="politics")

            member = disnake.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Player auto-role reaction remove"""
        message_id = payload.message_id
        if message_id == REACT_MESSAGE_ID:
            guild_id = payload.guild_id
            guild = disnake.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            if payload.emoji.name == "thonk":
                role = disnake.utils.get(guild.roles, name="Player")

            member = disnake.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.remove_roles(role)
        elif message_id == MULTIPLAYER_MESSAGE_ID:
            guild_id = payload.guild_id
            guild = disnake.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            if payload.emoji.name == "florrypog":
                role = disnake.utils.get(guild.roles, name="MP Member")

            member = disnake.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.remove_roles(role)
        elif message_id == POLITICS_MESSAGE_ID:
            guild_id = payload.guild_id
            guild = disnake.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

            if payload.emoji.name == "there_was_no_meme":
                role = disnake.utils.get(guild.roles, name="politics")

            member = disnake.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """Message delete event"""
        if payload.guild_id != EMF_SERVER_ID:
            return
        message = payload.cached_message
        url = message.author.avatar.url if message.author.avatar is not None else message.author.default_avatar.url
        # Text
        await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
            embed=(
                disnake.Embed(
                    description=f"**Message sent by {message.author.mention} deleted in {self.bot.get_channel(payload.channel_id).mention}**\n{message.content}",
                    color=0xFF470F,
                    timestamp=datetime.datetime.now(),
                )
                .set_author(
                    name=f"{message.author.name}#{message.author.discriminator}",
                    icon_url=url,
                )
                .set_footer(text=f"Author: {message.author.id} | Message ID: {payload.message_id}")
            )
        )
        # Attachments
        if message.attachments:
            for attachment in message.attachments:
                await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
                    embed=(
                        disnake.Embed(
                            description=f"**Attachment sent by {message.author.mention} deleted in {self.bot.get_channel(payload.channel_id).mention}**",
                            color=0xFF470F,
                            timestamp=datetime.datetime.now(),
                        )
                        .set_author(
                            name=f"{message.author.name}#{message.author.discriminator}",
                            icon_url=url,
                        )
                        .set_footer(text=f"Author: {message.author.id} | Message ID: {payload.message_id}")
                        .set_image(url=attachment.url)
                    )
                )
        # TODO: Once message cache saving is done, retrieve message data from there instead of internal cache

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        """Bulk message delete event"""
        # Send to action logs
        if payload.guild_id != EMF_SERVER_ID:
            return
        guild = self.bot.get_guild(payload.guild_id)
        await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
            embed=(
                disnake.Embed(
                    description=f"**Bulk Delete in {self.bot.get_channel(payload.channel_id).mention}, {len(payload.cached_messages)} messages deleted**",
                    color=0x337FD5,
                    timestamp=datetime.datetime.now(),
                ).set_author(
                    name=f"{guild.name}",
                    icon_url=guild.icon.url,
                )
            )
        )
        # TODO: Save to file for records (exclude messages from bots & the clean command)

        # TODO: Once message cache saving is done, retrieve message data from there instead of internal cache

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """Message edit event"""
        if payload.guild_id != EMF_SERVER_ID:
            return
        before = payload.cached_message
        after = await self.bot.get_channel(payload.channel_id).fetch_message(payload.data["id"])
        before_content = before.content if before is not None else ""
        if before_content == after.content:
            return
        url = after.author.avatar.url if after.author.avatar is not None else after.author.default_avatar.url
        await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
            embed=(
                disnake.Embed(
                    description=f"**Message edited in {after.channel.mention}** [Jump to Message]({after.jump_url})",
                    color=0x337FD5,
                    timestamp=datetime.datetime.now(),
                )
                .set_author(
                    name=f"{after.author.name}#{after.author.discriminator}",
                    icon_url=url,
                )
                .set_footer(text=f"User ID: {after.author.id}")
                .add_field(name="**Before**", value=f"{before_content}", inline=False)
                .add_field(name="**After**", value=f"{after.content}", inline=False)
            )
        )
        # TODO: Once message cache saving is done, retrieve message data from there instead of internal cache

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Member update event"""
        if before.guild.id != EMF_SERVER_ID:
            return
        roles_before, roles_after = before.roles, after.roles
        url = after.avatar.url if after.avatar is not None else after.default_avatar.url
        # Role add
        if len(roles_after) > len(roles_before):
            for role in roles_after:
                if role not in roles_before:
                    await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
                        embed=(
                            disnake.Embed(
                                description=f"**{after.mention} was given the `{role.name}` role**",
                                color=0x337FD5,
                                timestamp=datetime.datetime.now(),
                            )
                            .set_author(
                                name=f"{after.name}#{after.discriminator}",
                                icon_url=url,
                            )
                            .set_footer(text=f"ID: {after.id}")
                        )
                    )
                    break
        # Role remove
        elif len(roles_before) > len(roles_after):
            for role in roles_before:
                if role not in roles_after:
                    await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
                        embed=(
                            disnake.Embed(
                                description=f"**{after.mention} had the `{role.name}` role removed**",
                                color=0x337FD5,
                                timestamp=datetime.datetime.now(),
                            )
                            .set_author(
                                name=f"{after.name}#{after.discriminator}",
                                icon_url=url,
                            )
                            .set_footer(text=f"ID: {after.id}")
                        )
                    )
                    break
        # Nickname change
        elif before.nick != after.nick:
            before_nick = before.name if before.nick is None else before.nick
            after_nick = after.name if after.nick is None else after.nick
            await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
                embed=(
                    disnake.Embed(
                        description=f"**{after.mention} changed their nickname**",
                        color=0x337FD5,
                        timestamp=datetime.datetime.now(),
                    )
                    .set_author(
                        name=f"{after.name}#{after.discriminator}",
                        icon_url=url,
                    )
                    .set_footer(text=f"ID: {after.id}")
                    .add_field(name="**Before**", value=f"{before_nick}", inline=False)
                    .add_field(name="**After**", value=f"{after_nick}", inline=False)
                )
            )
        # Timeout given
        elif before.current_timeout is None and after.current_timeout is not None:
            expiry = relativedelta.relativedelta(after.current_timeout, datetime.datetime.now(datetime.timezone.utc))
            day, hour, minute, second, microsecond = (
                expiry.days,
                expiry.hours,
                expiry.minutes,
                expiry.seconds,
                expiry.microseconds,
            )
            second += microsecond / 1000000
            week = day // 7
            week_ln = f"{week} weeks, " if week > 1 else f"{week} week, "
            hour_ln = f"{hour} hours, " if hour > 1 else f"{hour} hour, "
            minute_ln = f"{minute} minutes, " if minute > 1 else f"{minute} minute, "
            second_ln = f"{second} seconds" if second > 1 else f"{second} second"
            day = day % 7
            day_ln = f"{day} days, " if day > 1 else f"{day} day, "
            if week > 0:
                expiry_ln = f"{week_ln}{day_ln}{hour_ln}{minute_ln}{second_ln}"
            elif day > 0:
                expiry_ln = f"{day_ln}{hour_ln}{minute_ln}{second_ln}"
            elif hour > 0:
                expiry_ln = f"{hour_ln}{minute_ln}{second_ln}"
            elif minute > 0:
                expiry_ln = f"{minute_ln}{second_ln}"
            else:
                expiry_ln = f"{second_ln}"
            await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
                embed=(
                    disnake.Embed(
                        description=f"**{after.mention} has been timed out**\nExpires in: {expiry_ln}",
                        color=0x337FD5,
                        timestamp=datetime.datetime.now(),
                    )
                    .set_author(
                        name=f"{after.name}#{after.discriminator}",
                        icon_url=url,
                    )
                    .set_footer(text=f"ID: {after.id}")
                )
            )
        # Timeout removed
        elif before.current_timeout is not None and after.current_timeout is None:
            await self.bot.get_channel(ACTION_LOG_CHANNEL_ID).send(
                embed=(
                    disnake.Embed(
                        description=f"**{after.mention}'s timeout has been removed**",
                        color=0x337FD5,
                        timestamp=datetime.datetime.now(),
                    )
                    .set_author(
                        name=f"{after.name}#{after.discriminator}",
                        icon_url=url,
                    )
                    .set_footer(text=f"ID: {after.id}")
                )
            )


def setup(bot):
    bot.add_cog(Events(bot))
