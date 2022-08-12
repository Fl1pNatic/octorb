import discord
from discord.ext import commands
import random

error_messages = ["No perms?", "You got no perms", "haha **no** (permissions)", "You don't have permissions to do this", "h-hiii you cant execute this command uwu"]

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, arg=None):
        if ctx.message.author.guild_permissions.manage_messages:
            if arg == None:
                await ctx.reply("cmon make me say smth")
                return
            await ctx.message.delete()
            await ctx.send(arg)
        else:
            await ctx.reply("I am not saying whatever you want me to say")

    @commands.command()
    async def pin(self, ctx, pinID=None):
        e=random.choice(tuple(error_messages))
        if ctx.message.author.guild_permissions.manage_messages:
            if pinID == None:
                await ctx.reply("You gotta supply id of the message as well")
            pinM = await ctx.fetch_message(int(pinID))
            if pinM.pinned == False:
                await pinM.pin()
            else:
                await pinM.unpin()
        else:
            await ctx.reply(e)

    @commands.command()
    async def delete(self, ctx, mID=None):
        e=random.choice(tuple(error_messages))
        if ctx.message.author.guild_permissions.manage_messages:
            deleteM = await ctx.fetch_message(mID)
            await deleteM.delete()
            await ctx.message.delete()
        else:
            await ctx.reply(e)

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        e=random.choice(tuple(error_messages))
        if ctx.message.author.guild_permissions.kick_members:
            if member == None:
                await ctx.reply("Specify who you want to kick")
                return
            await ctx.member.send(f"You were kicked from Will You Craft Server, reason: {reason}")
            await member.kick(reason=reason)
            await ctx.reply(f"Member kicked: `{reason}`")
        else:
            await ctx.reply(e)

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        e=random.choice(tuple(error_messages))
        if ctx.message.author.guild_permissions.ban_members:
            await ctx.member.send(f"You were banned from Will You Craft Server, reason: {reason}")
            await member.ban(reason=reason)
            await ctx.reply(f"Member banned: `{reason}`")
        else:
            await ctx.reply(e)            
