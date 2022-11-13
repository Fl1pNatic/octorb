import datetime
import random
import time
import typing

import discord
from discord import app_commands
from discord.ext import commands

error_messages = ["No perms?", "You got no perms",
                  "haha **no** (permissions)", "You don't have permissions to do this", "h-hiii you cant execute this command uwu"]


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Makes the bot say anything you want.")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, phrase):
        """
        Parameters
        ------------
        phrase
            The thing you want bot to say
        """
        await ctx.reply("Sent", ephemeral=True)
        await ctx.channel.send(phrase)
        await ctx.message.delete()

    @commands.hybrid_command(description="Pins specified message.")
    @commands.has_permissions(manage_messages=True)
    async def pin(self, ctx, message: discord.Message):
        """
        Parameters
        ------------
        message
            Message you want to pin (ID)
        """
        if message.pinned:
            await message.unpin()
            await ctx.reply("Unpinned message.")
            return
        await message.pin()
        await ctx.reply("Pinned message.")

    @commands.hybrid_command(description="Deletes specified message.")
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, message: discord.Message):
        """
        Parameters
        ------------
        message
            Message you want to delete (ID)
        """
        await message.delete()
        await ctx.reply("Deleted message.", ephemeral=True)
        await ctx.message.delete()

    @commands.hybrid_command(description="Kicks specified member.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Parameters
        ------------
        member
            User you want to kick (ID or Ping)
        reason
            Reason for kicking (Text)
        """
        embed = discord.Embed(
            title=f"Kicked {member.name + member.discriminator}", color=0xda7dff)
        embed.description = f"Reason: {reason}"
        try:
            await member.send(f"You were kicked from {ctx.guild.name}, {f'Reason: {reason}' if reason is not None else 'No reason was given.'}")
        except:
            await ctx.reply("Unable to message user.")
        await ctx.reply(embed=embed)
        await member.kick(reason=reason if reason is not None else 'No reason was given.')

    @commands.hybrid_command(description="Bans specified member.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Parameters
        ------------
        member
            User you want to ban
        reason
            Reason for banning
        """
        embed = discord.Embed(
            title=f"Banned {member.name + member.discriminator}", color=0xda7dff)
        embed.description = f"Reason: {reason}"
        try:
            await member.send(f"You were banned from {ctx.guild.name}, {f'Reason: {reason}' if reason is not None else 'No reason was given.'}")
        except:
            await ctx.reply("Unable to message user.")
        await ctx.reply(embed=embed)
        await member.ban(reason=reason if reason is not None else 'No reason was given.')

    @commands.hybrid_command(description="Unbans a specified banned member.")
    @commands.has_permissions(ban_members=True)
    async def pardon(self, ctx: commands.Context, member: int):
        """
        Parameters
        ------------
        member
            User you want to unban
        """
        bans = await ctx.guild.bans()
        banned_users = [user.user.id for user in bans]
        if member in banned_users:
            await ctx.guild.unban(bans[banned_users.index(member)].user)
            await ctx.reply(f"Member pardoned.")
        else:
            await ctx.reply("User does not appear to be banned.")

    @commands.hybrid_command(description="Purges messages from a channel from the past two weeks.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.context, max: typing.Optional[int], from_user: typing.Optional[discord.Member]):
        """
        Parameters
        ------------
        max
            The most messages this will delete
        from_user
            The user it will purge from
        """
        if max is None or max > 100:
            max = 100

        def purgeUserCheck(message):
            if message.author == from_user:
                return True
            return False
        if from_user is not None:
            messageCount = len(await ctx.channel.purge(oldest_first=False, limit=max, bulk=True, check=purgeUserCheck, after=datetime.datetime.fromtimestamp(int(time.time()-1209600))))
            await ctx.send(f"Purged {messageCount} messages.")
            return
        messageCount = len(await ctx.channel.purge(oldest_first=False, limit=max, bulk=True, after=datetime.datetime.fromtimestamp(int(time.time()-1209600))))
        await ctx.send(f"Purged {messageCount} messages.")

    @commands.hybrid_command(description="Clears the channel completely.")
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx: commands.Context):
        newChannel = await ctx.channel.clone()
        await ctx.channel.delete()
        await newChannel.send("Channel cleared.")

    @pardon.error
    async def pardon_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.reply("Error pardoning member.")
