from typing import ItemsView, OrderedDict
import discord
from discord.ext import commands
import git, os

from PermissionsChecks import permissionChecks

class other(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        hEmbed = discord.Embed(title="Help", description="Here you can find the list of all commands!", color=0xda7dff)

        cogs = self.bot.cogs
        cogs = [cog for cog in cogs.values()]
        cogs.sort(key=lambda cog:cog.qualified_name)
        for cog in cogs:
            hEmbed.add_field(name=cog.qualified_name.capitalize(), value=", ".join([command.name for command in cog.get_commands() if command.hidden is False ]))
        await ctx.reply(embed=hEmbed)

    @commands.command(hidden=True)
    @permissionChecks.developer()
    async def eval(self, ctx, *, command):
        await ctx.reply(eval(command))

    @commands.command()
    async def about(self, ctx):
        aEmbed = discord.Embed(title="About Octorb", description="Some information about the bot", color=0xda7dff)
        aEmbed.add_field(name="History", value="""The bot was originally made for a Minecraft SMP Discord server.
        It was started on 8th of August 2022 and renamed to Octorb on 14th of August 2022""", inline=False)
        aEmbed.add_field(name="Source", value="""This bot is **open-source** which means that anyone can contribute to it.

        You can find the source code here - <https://github.com/Fl1pNatic/octorb>
        And the trello board here - <https://trello.com/b/lJZJeVpl/octorb>
        """, inline=False)

        aEmbed.add_field(name="Statistics", value=f"""Server count: {len(self.bot.guilds)-10}""")

        aEmbed.add_field(name="Technical", value=f"""discord.py version: {discord.__version__}
       """)
        await ctx.reply(embed=aEmbed)

    @commands.command()
    async def changelog(self, ctx):
        repo: git.Git = git.Git(os.path.dirname(__file__))
        commits = repo.log('--pretty=%s').split("\n")[:10]
        commitsHashes = repo.log('--pretty=%h').split("\n")[:10]
        embed = discord.Embed(title="Changelog", color=0xff00bb)
        for commit in range(len(commits)):
            embed.add_field(name="`"+commitsHashes[commit]+"`", value="`"+commits[commit]+"`", inline=False)

        await ctx.reply(embed=embed)
