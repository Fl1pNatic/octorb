
import importlib
import os
import sys
import typing
import traceback
import git
import discord
from discord.ext import commands
import re

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

    @commands.command(description="Exec()s the command.")
    async def exec(self, ctx: commands.Context, *, code: str):
        """
        Parameters
        ------------
        command
            The command to run. Better not be anything bad or imma get you
        """
        if code.startswith('```'):
            code = code.strip('```').partition('\n')[2].strip()  # Remove multiline code blocks
        else:
            code = code.strip('`').strip()

        e = discord.Embed(type='rich')
        e.add_field(name='Code', value=f'```py\n{code}\n```', inline=False)
        try:
            locals_ = locals()
            load_function(code, locals_)
            ret = await locals_['evl_func'](ctx)

            e.title = 'Success'
            retr_str = f'{ret!r} ({type(ret).__name__})'
            e.add_field(name='Output', value=f'```\n{retr_str if len(retr_str) < 1010 else retr_str[:1010] + "..."}\n```', inline=False)
        except Exception as err:
            e.title = 'Error'
            retr_str = repr(err)
            e.add_field(name='Error', value=f'```\n{retr_str if len(retr_str) < 1010 else retr_str[:1010] + "..."}\n```')
        await ctx.send('', embed=e)

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

def load_function(code: str, locals_):
    """Loads the user-evaluted code as a function so it can be executed."""
    function_header = 'async def evl_func(ctx):'

    lines = code.splitlines()
    if len(lines) > 1:
        indent = 4
        for line in lines:
            line_indent = re.search(r'\S', line).start()
            if line_indent:
                indent = line_indent
                break
        line_sep = '\n' + ' ' * indent
        exec(function_header + line_sep + line_sep.join(lines), locals_)
    else:
        try:
            exec(function_header + '\n\treturn ' + lines[0], locals_)
        except SyntaxError as err:
            if err.text[err.offset - 1] == '=' or err.text[err.offset - 3:err.offset] == 'del' \
                    or err.text[err.offset - 6:err.offset] == 'return':
                exec(function_header + '\n\t' + lines[0], locals_)
            else:
                raise err

async def setup(bot):
    await bot.add_cog(developer(bot))