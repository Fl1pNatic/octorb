import datetime
import random
import time
import typing

import discord
from discord.ext import commands

error_messages = ["No perms?", "You got no perms",
                  "haha **no** (permissions)", "You don't have permissions to do this", "h-hiii you cant execute this command uwu"]


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Makes the bot say anything you want.")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, phrase: str):
        """
        Parameters
        ------------
        phrase
            The thing you want bot to say
        """
        await ctx.channel.send(phrase)
        await ctx.message.delete()
    
    @commands.command(description="Makes the bot say anything you want in a specific channel.")
    @commands.has_permissions(manage_messages=True)
    async def sayin(self, ctx: commands.Context, channel: discord.TextChannel, *, phrase: str):
        """
        Parameters
        ------------
        channel
            The channel you want bot to say in
        phrase
            The thing you want bot to say
        """
        await channel.send(phrase)
        await ctx.message.delete()

    @commands.command(description="Pins specified message.")
    @commands.has_permissions(manage_messages=True)
    async def pin(self, ctx: commands.Context, message: int):
        """
        Parameters
        ------------
        message
            Message you want to pin (ID)
        """
        if ctx.message.type != discord.MessageType.reply:
            print("Reply")
        message = await ctx.channel.fetch_message(message)
        if message.pinned:
            await message.unpin()
            await ctx.send("Unpinned message.")
            return
        await message.pin()
        await ctx.send("Pinned message.")

    @commands.command(description="Deletes specified message.")
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx: commands.Context, message: int):
        """
        Parameters
        ------------
        message
            Message you want to delete (ID)
        """
        message = await ctx.channel.fetch_message(message)
        await message.delete()
        await ctx.send("Deleted message.", ephemeral=True)
        await ctx.message.delete()

    @commands.command(description="Kicks specified member.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str="No reason was given."):
        """
        Parameters
        ------------
        member
            User you want to kick (ID or Ping)
        reason
            Reason for kicking (Text)
        """
        if (member.top_role > ctx.guild.get_member(ctx.bot.user.id).top_role) or (member == ctx.guild.owner):
            await ctx.send("Could not kick member.")
            return

        embed = discord.Embed(
            title=f"Kicked {member.name}#{member.discriminator}", 
            color=0xda7dff, 
            description = f"Reason: {reason}")
        try:
            await member.send(f"You were kicked from {ctx.guild.name}, {f'Reason: {reason}'}")
        except:
            await ctx.send("Unable to message user.")
        try:
            await member.kick(reason=reason)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Could not kick member.")
            return

    @commands.command(description="Bans specified member.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason:str="No reason was given."):
        """
        Parameters
        ------------
        member
            User you want to ban
        reason
            Reason for banning
        """
        if (member.top_role > ctx.guild.get_member(ctx.bot.user.id).top_role) or (member == ctx.guild.owner):
            await ctx.send("Could not ban member.")
            return

        embed = discord.Embed(
            title=f"Banned {member.name}#{member.discriminator}", 
            color=0xda7dff, 
            description = f"Reason: {reason}")
        try:
            await member.send(f"You were banned from {ctx.guild.name}, {f'Reason: {reason}'}")
        except:
            await ctx.send("Could not message member.")
        try:
            await member.ban(reason=reason)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Could not ban member.")
            return


    @commands.command(description="Unbans a specified banned member.")
    @commands.has_permissions(ban_members=True)
    async def pardon(self, ctx: commands.Context, member: discord.Member):
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
            await ctx.send(f"Member pardoned.")
        else:
            await ctx.send("User does not appear to be banned.")

    @commands.command(description="Purges messages from a channel from the past two weeks.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, max: typing.Optional[int], from_user: typing.Optional[discord.Member]):
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

    @commands.command(description="Clears the channel completely.")
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx: commands.Context):
        newChannel = await ctx.channel.clone()
        await ctx.channel.delete()
        await newChannel.send("Channel cleared.")

    @pardon.error
    async def pardon_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("Error pardoning member.")

async def setup(bot):
    await bot.add_cog(moderation(bot))