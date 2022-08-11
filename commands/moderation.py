import nextcord
from nextcord.ext import commands

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx):
        if ctx.message.author.guild_permissions.manage_messages:
            # this particular here i need to make it like this coz i need more than the first argument
            pref = ctx.message.content.split(" ")[0]
            cont = ctx.message.content + " "
            mes = cont[len(pref):-1]
            await ctx.message.delete()
            await ctx.send(mes)
        else:
            await ctx.reply("I am not saying whatever you want me to say")

    @commands.command()
    async def pin(self, ctx):
        if ctx.message.author.guild_permissions.manage_messages:
            pinArg = ctx.message.content.split(" ")[1]
            pinM = await ctx.fetch_message(int(pinArg))
            if pinM.pinned == False:
                await pinM.pin()
            else:
                await pinM.unpin()
        else:
            await ctx.reply("You cannot use this command")

    @commands.command()
    async def mdelete(self,ctx):
        if ctx.message.author.guild_permissions.manage_messages:
            delArg = ctx.message.content.split(" ")[1]
            deleteM = await ctx.fetch_message(int(delArg))
            await deleteM.delete()
            await ctx.message.delete()
        else:
            await ctx.reply("You cannot use this command")

    @commands.command()
    async def kick(self, ctx, member: nextcord.Member, *, reason=None):
        if ctx.message.author.guild_permissions.kick_members:
            await ctx.member.send(f"You were kicked from WYS MC Server, reason: {reason}")
            await member.kick(reason=reason)
            await ctx.reply(f"Member kicked: `{reason}`")
        else:
            await ctx.reply("You cannot use this command")
