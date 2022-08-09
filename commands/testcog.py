import nextcord
from nextcord.ext import commands

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("test lmao fuck off actually")