import nextcord
from nextcord.ext import commands

help_embed = nextcord.Embed(title="Help",
                            description="What each command does",
                            color=0xff00bb)

help_embed.add_field(name="Fun",
    value="ask | gallery | coinflip",
    inline=False)

help_embed.add_field(name="Moderation",
 value="say | pin | delete | kick | ban",
 inline=False)

help_embed.add_field(name="Other",
 value="help | source | minecraft",
 inline=False)

class other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=help_embed)

    @commands.command()
    async def source(self, ctx):
        await ctx.send("This bot is **open-source** which means that anyone can contribute to it.\n\nYou can find the source code here - <https://github.com/Fl1pNatic/squidcraftbot>")

    @commands.command()
    async def minecraft(self, ctx):
        await ctx.send("You can join the server using this IP: 132.145.106.236\n\nNo cracked accounts. Minecraft 1.19")

                
