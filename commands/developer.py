
import importlib
import os
import sys
import typing

import git
import discord
from discord.ext import commands

from PermissionsChecks import devCheck, permissionErrors


async def loadModule(module, ctx):
    if module in ctx.bot.cogs:
        await ctx.reply("You can't load a module that's already loaded ffs.")
        return
    try:
        importlib.import_module("commands."+module)
    except (ImportError) as error:
        await ctx.reply("Error loading module. "+error.msg)
        return
    try:
        await ctx.bot.add_cog(sys.modules[f"commands.{module}"].__getattribute__(f"{module}")(ctx.bot))
    except (AttributeError) as error:
        await ctx.reply("Error loading module. "+error.name)
        return
    await ctx.reply("Loaded module.")


async def unloadModule(module, ctx):
    if not module in ctx.bot.cogs:
        await ctx.reply("Module not loaded.")
        print(self, ctx.bot.cogs)
        return
    await ctx.bot.remove_cog(module)
    print("hwhoehwoi")
    del sys.modules["commands."+module]
    await ctx.reply("Module unloaded.")


async def gitupdate():
    repo: git.Repo = git.Repo(os.path.dirname(__file__ )+ "/..")
    for remote in repo.remotes:
        remote.pull()


class developer(commands.Cog):
    def cog_check(self, ctx):
        if devCheck(ctx):
            return True
        raise permissionErrors.NonDeveloperError
    

    @commands.hybrid_command(description="Loads the given module.")
    async def loadmodule(self, ctx: commands.Context, module_name: str):
        """
        Parameters
        ------------
        module_name
            The name of the module you want to load.
        """
        await loadModule(module_name, ctx)


    @commands.hybrid_command(description="Unloads the given module.")
    async def unloadmodule(self, ctx: commands.Context, module_name: str):
        """
        Parameters
        ------------
        module_name
            The name of the module you want to unload.
        """
        await unloadModule(module_name, ctx)


    @commands.hybrid_command(description="Reloads the given module.")
    async def reloadmodule(self, ctx: commands.Context, module_name: str):
        """
        Parameters
        ------------
        module_name
            The name of the module you want to reload.
        """
        await unloadModule(module_name, ctx)
        await loadModule(module_name, ctx)


    @commands.hybrid_command(description="Update the bot from github.")
    async def update(self, ctx: commands.Context):
        await gitupdate()
        await ctx.reply("Pulled Changes")


    @commands.command(description="Sync the slash commands.")
    @commands.guild_only()
    async def sync(
            self, ctx: commands.Context, spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
        """
        Parameters
        ------------
        spec
            Where to sync. None for everywhere, ~ for the current guild, * to copy the global to the current guild, ^ to delete the current guilds.
        """
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()
        print(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    @commands.hybrid_command(description="Eval()s the command.")
    async def eval(self, ctx: commands.Context, *, command: str):
        """
        Parameters
        ------------
        command
            The command to run. Better not be anything bad or imma get you.
        """
        try:
            await ctx.reply(await eval(command))
        except Exception as ex:
            await ctx.reply(ex)

    @commands.hybrid_command(description="Exec()s the command.")
    async def exec(self, ctx: commands.Context, *, command: str):
        """
        Parameters
        ------------
        command
            The command to run. Better not be anything bad or imma get you.
        """
        try:
            exec(command)
            await ctx.reply("Execution complete.")
        except Exception as ex:
            await ctx.reply(ex)

    @commands.hybrid_command(description="Changes Octorb's profile picture to the attached image.")
    async def setpfp(self, ctx: commands.Context, image: discord.Attachment):
        if not image.content_type.startswith("image"):
            await ctx.reply("Attachement must be an image.")
            return
        try:
            picData = await image.read()
            await ctx.bot.user.edit(avatar=picData)
            await ctx.reply("Avatar updated!")
        except Exception as e:
            await ctx.reply(e)
            
