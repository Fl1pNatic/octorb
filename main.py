import discord
import importlib
import sys
from discord.ext import commands as botCommands
from dotenv import dotenv_values, load_dotenv
import git
import os
import pymysql
from PermissionsChecks import permissionErrors, permissionChecks, devCheck
from commands.fun import fun
from commands.math import math
from commands.moderation import moderation
from commands.other import other
from commands.xp import xp
from commands.dynamic import dynamic
import typing

sys.path.append(".")


load_dotenv()
TOKEN = dotenv_values()["TOKEN"]

command_prefix = ["oc!", "!", "o!"] if not "DEVMODE" in dotenv_values() else ["t!"]
bot = botCommands.Bot(command_prefix=command_prefix,
                    activity=discord.Activity(type=discord.ActivityType.watching, name="oc! | o! | !help for commands list"),
                   intents=discord.Intents.all(),
                   help_command=None,
                   case_insensitive=True
                   )
db = None
if not "DEVMODE" in dotenv_values():
    db = pymysql.connect(host=dotenv_values()['DBHOST'], user=dotenv_values()['DBUSERNAME'], password=dotenv_values()['DBPASSWORD'], database=dotenv_values()['DB'])


setattr(bot,"db", db)


@bot.event
async def on_ready():
    await gitupdate()
    await bot.add_cog(fun(bot))
    await bot.add_cog(xp(bot))
    await bot.add_cog(other(bot))
    await bot.add_cog(moderation(bot))
    await bot.add_cog(math(bot)) # too annoying
    await bot.add_cog(dynamic(bot))
    print(f"It's {bot.user}in' time")

@bot.event
async def on_disconnect():
    print("Disconnected from Discord")

@bot.event
async def on_message(message: discord.Message):
    if message.guild == None:
        if message.author.bot:
            return
        await message.channel.send("You are not allowed to use the bot in DMs")
        return
    await bot.process_commands(message)

# Helper Commands
async def getuser(userid, guildid):
    guild = bot.get_guild(guildid)
    user = await guild.fetch_member(userid)
    return user


async def loadModule(module, ctx):
    if module in bot.cogs:
        await ctx.reply("You can't load a module that's already loaded ffs.")
        return
    try:
        importlib.import_module("commands."+module)
    except(ImportError) as error:
        await ctx.reply("Error loading module. "+error.msg)
        return
    try:
        await bot.add_cog(sys.modules[f"commands.{module}"].__getattribute__(f"{module}")(bot))
    except(AttributeError) as error:
        await ctx.reply("Error loading module. "+error.name)
        return
    await ctx.reply("Loaded module.")

async def unloadModule(module, ctx):
    if not module in bot.cogs:
        await ctx.reply("Module not loaded.")
        return
    await bot.remove_cog(module)
    del sys.modules["commands."+module]
    await ctx.reply("Module unloaded.")

async def gitupdate():
    repo: git.Repo = git.Repo(os.path.dirname(__file__))
    for remote in repo.remotes:
        remote.pull()


@bot.hybrid_command()
@permissionChecks.developer()
async def loadmodule(ctx:botCommands.Context, module_name:str):
    await loadModule(module_name, ctx)


@bot.hybrid_command()
@permissionChecks.developer()
async def unloadmodule(ctx:botCommands.Context, module_name:str):
    await unloadModule(module_name, ctx)

@bot.hybrid_command()
@permissionChecks.developer()
async def reloadmodule(ctx:botCommands.Context, module_name:str):
    await unloadModule(module_name, ctx)
    await loadModule(module_name, ctx)

@bot.hybrid_command()
@permissionChecks.developer()
async def update(ctx:botCommands.Context):
    await gitupdate()
    await ctx.reply("Pulled Changes")

@bot.command()
@botCommands.guild_only()
@permissionChecks.developer()
async def sync(
  ctx: botCommands.Context, spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
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
    print(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
    await ctx.send(
        f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
    )
    return
    
@bot.event
async def on_command_error(ctx, error):
    match type(error):
        case permissionErrors.NonDeveloperError:
            await ctx.reply("This command is limited to Octorb Developers.")
        case botCommands.errors.MissingRequiredArgument:
            await ctx.reply(f"Missing argument: {error.param.name.capitalize()}" )
        case botCommands.errors.CommandNotFound:
            pass
        case botCommands.errors.CommandInvokeError:
            if isinstance(error.original, discord.errors.HTTPException):
                print(error.original.code)
                if error.original.code == 50035:
                    await ctx.reply("it's too big daddy, it won't fit~")
                    print(error.original.text)
                    return
                raise(error)
        case botCommands.errors.MissingPermissions:
            perms = error.missing_permissions
            await ctx.reply(f"You are missing the following permissions needed to use this command: {' '.join(str(x) for x in perms)}")
        case _: raise(error)

@bot.check
async def botperms_check(ctx: botCommands.Context):
    guild = ctx.guild
    me = guild.me if guild is not None else ctx.bot.user
    permissions = ctx.channel.permissions_for(me)

    if getattr(permissions, "send_messages") is False:
        raise botCommands.BotMissingPermissions(["send_messages"])
    return True

if "DEVMODE" in dotenv_values():
    @bot.check
    async def devckeck(ctx: botCommands.Context):
        if devCheck(ctx):
            return True
        

bot.run(TOKEN)
