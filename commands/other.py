import nextcord
from nextcord.ext import commands
import git, os

help_embed = nextcord.Embed(title="Help",
                            description="What each command does",
                            color=0xff00bb)

help_embed.add_field(name="Fun",
    value="ask | gallery | coinflip | rng1000 | yo",
    inline=False)

help_embed.add_field(name="Moderation",
 value="say | pin | delete | kick | ban",
 inline=False)

help_embed.add_field(name="Math",
 value="math | rng1000 | coinflip",
 inline=False)

help_embed.add_field(name="XP",
 value="xp | xptop | givexp",
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

    @commands.command()
    async def changelog(self, ctx):
        repo: git.Git = git.Git(os.path.dirname(__file__))
        commits = repo.log('--pretty=%s').split("\n")[:10]
        commitsHashes = repo.log('--pretty=%h').split("\n")[:10]
        embed = nextcord.Embed(title="Changelog", color=0xff00bb)
        for commit in range(len(commits)):
            embed.add_field(name="`"+commitsHashes[commit]+"`", value="`"+commits[commit]+"`", inline=False)

        await ctx.send(embed=embed)


                
