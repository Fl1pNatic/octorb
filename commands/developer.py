
import importlib
import os
import sys
import typing
import traceback
import git
import discord
from discord.ext import commands

from PermissionsChecks import devCheck, permissionErrors

class developer(commands.Cog):
    def cog_check(self, ctx):
        if devCheck(ctx):
            return True
        raise permissionErrors.NonDeveloperError
    

    @commands.command(description="Loads the given module.")
    async def loadmodule(self, ctx: commands.Context, module_name: str):
        """
        Parameters
        ------------
        module_name
            The name of the module you want to load
        """
        try:
            await ctx.bot.load_extension("commands."+module_name)
            await ctx.reply("Loaded extension")
        except Exception as e :
            match type(e):
                case commands.ExtensionNotFound:
                    await ctx.reply("Extension not found.")
                case commands.ExtensionAlreadyLoaded:
                    await ctx.reply("Extension already loaded")
                case commands.NoEntryPointError:
                    await ctx.reply("No entry point to extension")
                case commands.ExtensionFailed:
                    await ctx.reply("Extension loading failed")
                    await ctx.reply(''.join(traceback.TracebackException.from_exception(e).format()))
                case _:
                    print(e)
                    await ctx.reply("Unknown error")



    @commands.command(description="Unloads the given module.")
    async def unloadmodule(self, ctx: commands.Context, module_name: str):
        """
        Parameters
        ------------
        module_name
            The name of the module you want to unload
        """
        try:
            await ctx.bot.unload_extension("commands."+module_name)
            await ctx.reply("Unloaded extension")
        except Exception as e :
            match type(e):
                case commands.ExtensionNotFound:
                    await ctx.reply("Extension not found.")
                case commands.ExtensionNotLoaded:
                    await ctx.reply("Extension not loaded")
                case _:
                    print(e)
                    await ctx.reply("Unknown error")


    @commands.command(description="Reloads the given module.")
    async def reloadmodule(self, ctx: commands.Context, module_name: str):
        """
        Parameters
        ------------
        module_name
            The name of the module you want to reload
        """
        try:
            await ctx.bot.reload_extension("commands."+module_name)
            await ctx.reply("Reloaded extension")
        except Exception as e :
            match type(e):
                case commands.ExtensionNotFound:
                    await ctx.reply("Extension not found.")
                case commands.ExtensionNotLoaded:
                    await ctx.reply("Extension not loaded")
                case commands.NoEntryPointError:
                    await ctx.reply("No entry point to extension")
                case commands.ExtensionFailed:
                    await ctx.reply("Extension loading failed")
                case _:
                    print(e.with_traceback)
                    await ctx.reply("Unknown error")

    @commands.command(description="Update the bot from github.")
    async def update(self, ctx: commands.Context):
        repo: git.Repo = git.Repo(os.path.dirname(__file__ )+ "/..")
        [remote.pull() for remote in repo.remotes]
        await ctx.reply("Pulled Changes")


    @commands.command(description="Sync the slash commands.")
    @commands.guild_only()
    async def sync(
            self, ctx: commands.Context, spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
        """
        Parameters
        ------------
        spec
            Where to sync. None for everywhere, ~ for the current guild, * to copy the global to the current guild, ^ to delete the current guilds
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

    @commands.command(description="Eval()s the command.")
    async def eval(self, ctx: commands.Context, *, command: str):
        """
        Parameters
        ------------
        command
            The command to run. Better not be anything bad or imma get you
        """
        try:
            await ctx.reply(await eval(command))
        except Exception as ex:
            await ctx.reply(ex)

    @commands.command(description="Exec()s the command.")
    async def exec(self, ctx: commands.Context, *, command: str):
        """
        Parameters
        ------------
        command
            The command to run. Better not be anything bad or imma get you
        """
        try:
            exec(command)
            await ctx.reply("Execution complete.")
        except Exception as ex:
            await ctx.reply(ex)

    @commands.command(description="Changes Octorb's profile picture to the attached image.")
    async def setpfp(self, ctx: commands.Context, image: discord.Attachment):
        """
        Parameters
        ------------
        image
            The image to set the pfp to
        """
        if not image.content_type.startswith("image"):
            await ctx.reply("Attachement must be an image.")
            return
        try:
            picData = await image.read()
            await ctx.bot.user.edit(avatar=picData)
            await ctx.reply("Avatar updated!")
        except Exception as e:
            await ctx.reply(e)

async def setup(bot):
    await bot.add_cog(developer(bot))