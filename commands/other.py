import nextcord
from nextcord.ext import commands

help_embed = nextcord.Embed(title="Help",
                            description="What each command does",
                            color=0xff00bb)

help_embed.add_field(name="Fun",
    value="ask | squidgames | helloai | helloaiv1 | jonasspin | shellyspin ",
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
