import datetime
import random
import time
import typing

import discord
from discord import app_commands
from discord import app_commands
from discord.ext import commands

error_messages = ["No perms?", "You got no perms",
                  "haha **no** (permissions)", "You don't have permissions to do this", "h-hiii you cant execute this command uwu"]


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Makes the bot say anything you want.")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: discord.Interaction, phrase: str):
        """
        Parameters
        ------------
        phrase
            The thing you want bot to say
        """
        await ctx.response.send_message("Sent", ephemeral=True)
        await ctx.channel.send(phrase)
        await ctx.message.delete()

    @app_commands.command(description="Pins specified message.")
    @commands.has_permissions(manage_messages=True)
    async def pin(self, ctx: discord.Interaction, message: int):
        """
        Parameters
        ------------
        message
            Message you want to pin (ID)
        """
        message = await ctx.channel.fetch_message(message)
        if message.pinned:
            await message.unpin()
            await ctx.response.send_message("Unpinned message.")
            return
        await message.pin()
        await ctx.response.send_message("Pinned message.")

    @app_commands.command(description="Deletes specified message.")
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx: discord.Interaction, message: int):
        """
        Parameters
        ------------
        message
            Message you want to delete (ID)
        """
        message = await ctx.channel.fetch_message(message)
        await message.delete()
        await ctx.response.send_message("Deleted message.", ephemeral=True)
        await ctx.message.delete()

    @app_commands.command(description="Kicks specified member.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: discord.Interaction, member: discord.Member, *, reason: str="No reason was given."):
        """
        Parameters
        ------------
        member
            User you want to kick (ID or Ping)
        reason
            Reason for kicking (Text)
        """
        if (member.top_role > ctx.guild.get_member(ctx.client.user.id).top_role) or (member == ctx.guild.owner):
            await ctx.response.send_message("Could not kick member.")
            return

        embed = discord.Embed(
            title=f"Kicked {member.name}#{member.discriminator}", 
            color=0xda7dff, 
            description = f"Reason: {reason}")
        try:
            await member.send(f"You were kicked from {ctx.guild.name}, {f'Reason: {reason}'}")
        except:
            await ctx.response.send_message("Unable to message user.")
        try:
            await member.kick(reason=reason)
            await ctx.response.send_message(embed=embed)
        except:
            await ctx.response.send_message("Could not kick member.")
            return

    @app_commands.command(description="Bans specified member.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: discord.Interaction, member: discord.Member, *, reason:str="No reason was given."):
        """
        Parameters
        ------------
        member
            User you want to ban
        reason
            Reason for banning
        """
        if (member.top_role > ctx.guild.get_member(ctx.client.user.id).top_role) or (member == ctx.guild.owner):
            await ctx.response.send_message("Could not ban member.")
            return

        embed = discord.Embed(
            title=f"Banned {member.name}#{member.discriminator}", 
            color=0xda7dff, 
            description = f"Reason: {reason}")
        try:
            await member.send(f"You were banned from {ctx.guild.name}, {f'Reason: {reason}'}")
        except:
            await ctx.response.send_message("Could not message member.")
        try:
            await member.ban(reason=reason)
            await ctx.response.send_message(embed=embed)
        except:
            await ctx.response.send_message("Could not ban member.")
            return


    @app_commands.command(description="Unbans a specified banned member.")
    @commands.has_permissions(ban_members=True)
    async def pardon(self, ctx: discord.Interaction, member: discord.Member):
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
            await ctx.response.send_message(f"Member pardoned.")
        else:
            await ctx.response.send_message("User does not appear to be banned.")

    @app_commands.command(description="Purges messages from a channel from the past two weeks.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: discord.Interaction, max: typing.Optional[int], from_user: typing.Optional[discord.Member]):
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
            await ctx.response.send_message(f"Purged {messageCount} messages.")
            return
        messageCount = len(await ctx.channel.purge(oldest_first=False, limit=max, bulk=True, after=datetime.datetime.fromtimestamp(int(time.time()-1209600))))
        await ctx.response.send_message(f"Purged {messageCount} messages.")

    @app_commands.command(description="Clears the channel completely.")
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx: discord.Interaction):
        newChannel = await ctx.channel.clone()
        await ctx.channel.delete()
        await newChannel.send("Channel cleared.")

    @pardon.error
    async def pardon_error(self, ctx: discord.Interaction, error: Exception):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.response.send_message("Error pardoning member.")
