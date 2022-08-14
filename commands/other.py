import discord
from discord.ext import commands
import git, os

class other(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        hEmbed = discord.Embed(title="Help", description="Here you can find the list of all commands!", color=0xff00bb)

        for cogName, cog in self.bot.cogs.items():
            hEmbed.add_field(name=cogName.capitalize(), value=", ".join([command.name for command in cog.get_commands()]))
        await ctx.send(embed=hEmbed)

    @commands.command()
    async def source(self, ctx):
        await ctx.send("This bot is **open-source** which means that anyone can contribute to it.\n\nYou can find the source code here - <https://github.com/Fl1pNatic/squidcraftbot>")

    @commands.command()
    async def changelog(self, ctx):
        repo: git.Git = git.Git(os.path.dirname(__file__))
        commits = repo.log('--pretty=%s').split("\n")[:10]
        commitsHashes = repo.log('--pretty=%h').split("\n")[:10]
        embed = discord.Embed(title="Changelog", color=0xff00bb)
        for commit in range(len(commits)):
            embed.add_field(name="`"+commitsHashes[commit]+"`", value="`"+commits[commit]+"`", inline=False)

        await ctx.send(embed=embed)
