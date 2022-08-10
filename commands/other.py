import nextcord
from nextcord.ext import commands

help_embed = nextcord.Embed(title="Help",
                            description="What each command does",
                            color=0xff00bb)

help_embed.add_field(name="Fun",
    value="ask | gallery | squidgames | helloai | helloaiv1 | jonasspin | shellyspin  ",
    inline=False)

help_embed.add_field(name="Moderation",
 value="say | pin | mdelete",
 inline=False)

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=help_embed)

    @commands.command()
    async def source(self, ctx):
        await ctx.send("This bot is **open-source** which means that anyone can contribute to it.\n\nYou can find the source code here - <https://github.com/Fl1pNatic/squidcraftbot>")
