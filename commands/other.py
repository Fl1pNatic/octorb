from typing import ItemsView, OrderedDict
import discord
from discord.ext import commands
from discord import Button, ButtonStyle, app_commands
import git, os
import typing

from PermissionsChecks import permissionChecks

class other(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def help(self, ctx:commands.Context, command_name: typing.Optional[str]):
        if(command_name is None):
            hEmbed = discord.Embed(title="Help", description="Here you can find the list of all commands!", color=0xda7dff)
            cogs = self.bot.cogs
            cogs = [cog for cog in cogs.values()]
            cogs.sort(key=lambda cog:cog.qualified_name)
            for cog in cogs:
                hEmbed.add_field(name=cog.qualified_name.capitalize(), value=", ".join([command.name for command in cog.get_commands() if command.hidden is False ]))
            await ctx.reply(embed=hEmbed)
            return
        if(command_name not in ctx.bot.all_commands.keys()):
            await ctx.send("Command does not exist")
            return
        command: commands.Command = ctx.bot.all_commands[command_name]
        commandEmbed = discord.Embed(title=f"Help for `{command.name.capitalize()}`", description=command.description if len(command.description) > 0 else "Command has no description, please report this in the support server.")
        if(len(command.clean_params) > 0):
            params = []
            for param in command.clean_params.values():
                params.append(f"`{param.name.capitalize()}` `[{'Optional' if type(param.converter) == typing._UnionGenericAlias else 'Required'}]`:{param.description if hasattr(param, 'description') else 'Parameter not described, please report this.'}")
            commandEmbed.add_field(name="Paramaters", value="\n".join(params))
        await ctx.send(embed=commandEmbed)
                

    @commands.hybrid_command(hidden=True)
    @permissionChecks.developer()
    async def eval(self, ctx:commands.Context, *, command: str):
        try:
            await ctx.reply(await eval(command))
        except Exception as ex:
            await ctx.reply(ex)
    @commands.hybrid_command(hidden=True)
    @permissionChecks.developer()
    async def exec(self, ctx:commands.Context, *, command: str):
        try:
            exec(command)
            await ctx.reply("Execution complete.")
        except Exception as ex:
            await ctx.reply(ex)
    @commands.hybrid_command()
    async def about(self, ctx:commands.Context):
        aEmbed = discord.Embed(title="About Octorb", description="Some information about the bot", color=0xda7dff)
        aEmbed.add_field(name="History", value="""The bot was originally made for a Minecraft SMP Discord server.
        It was started on 8th of August 2022 and renamed to Octorb on 14th of August 2022""", inline=False)
        aEmbed.add_field(name="Source", value="""This bot is **open-source** which means that anyone can contribute to it.

        You can find the source code here - <https://github.com/x8c8r/octorb>
        And the trello board here - <https://trello.com/b/lJZJeVpl/octorb>

        Along with that, you can join the official support and feedback server here - <https://discord.gg/wEweHdyvy6>
        """, inline=False)

        aEmbed.add_field(name="Statistics", value=f"""Server count: {len(self.bot.guilds)-10}""")

        aEmbed.add_field(name="Technical", value=f"""discord.py version: {discord.__version__}
       """)
        await ctx.reply(embed=aEmbed)

    @commands.hybrid_command(description="Shows the most recent git commits that are included in the bot.")
    async def changelog(self, ctx:commands.Context):
        repo: git.Git = git.Git(os.path.dirname(__file__))
        commits = repo.log('--pretty=%s').split("\n")[:10]
        commitsHashes = repo.log('--pretty=%h').split("\n")[:10]
        embed = discord.Embed(title="Changelog", color=0xff00bb)
        for commit in range(len(commits)):
            embed.add_field(name="`"+commitsHashes[commit]+"`", value="`"+commits[commit]+"`", inline=False)

        await ctx.reply(embed=embed)

    @commands.command()
    async def test(self, ctx:commands.Context):
        view = discord.ui.View()
        button = Button(
            style=ButtonStyle.green,
            custom_id="yes",
            label="yup"
        )
        view.add_item(item=button)
        await ctx.send("here is your fucking button if there is one", view=view)
