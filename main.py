from inspect import Attribute
import nextcord
import importlib
import sys
from nextcord.ext import commands as botCommands
from dotenv import dotenv_values, load_dotenv
import git
import os
import mysql.connector
from commands.fun import fun
from commands.math import math
from commands.moderation import moderation
from commands.other import other
from commands.xp import xp




load_dotenv()
TOKEN = dotenv_values()["TOKEN"]

command_prefix = ["sq!", "!", "s!"] if not "DEVMODE" in dotenv_values() else ["t!"]
bot = botCommands.Bot(command_prefix=command_prefix,
                    activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="sq! | s! | !help for commands list"),
                   intents=nextcord.Intents.all(),
                   help_command=None)
db = None
if not "DEVMODE" in dotenv_values():
    db = mysql.connector.connect(host=dotenv_values()['DBHOST'], user=dotenv_values()['DBUSERNAME'], password=dotenv_values()['DBPASSWORD'], database=dotenv_values()['DB'])



bot.add_cog(fun(bot))
bot.add_cog(other(bot))
bot.add_cog(moderation(bot))
bot.add_cog(math(bot))
bot.add_cog(xp(bot, db))

@bot.event
async def on_ready():
    print(f"It's {bot.user}in' time")
    await gitupdate()

@bot.event
async def on_disconnect():
    print("Disconnected from Discord")

@bot.event
async def on_message(message: nextcord.Message):
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

@bot.event
async def on_member_join(member: nextcord.Member):
    guild = bot.get_guild(member.guild.id)
    role = nextcord.utils.get(guild.roles, name='Member')
    user = await getuser(member.id, member.guild.id)
    await user.add_roles(role)


async def loadModule(module, ctx):
    if module in bot.cogs:
        await ctx.send("You can't load a module that's already loaded ffs.")
        return
    try:
        importlib.import_module("commands."+module)
    except(ImportError) as error:
        await ctx.send("Error loading module. "+error.msg)
        return
    try:
        bot.add_cog(sys.modules[f"commands.{module}"].__getattribute__(f"{module}")(bot))
    except(AttributeError) as error:
        await ctx.send("Error loading module. "+error.name)
        return
    await ctx.send("Loaded module.")

async def unloadModule(module, ctx):
    if not module in bot.cogs:
        await ctx.send("Module not loaded.")
        return
    bot.remove_cog(module)
    del sys.modules["commands."+module]
    await ctx.send("Module unloaded.")

async def gitupdate():
    repo: git.Repo = git.Repo(os.path.dirname(__file__))
    for remote in repo.remotes:
        remote.pull()
    print("Pulled Changes")


@bot.command()
async def loadmodule(ctx:botCommands.Context, *args):
    if ctx.message.author.guild_permissions.manage_guild == False:
        await ctx.send("You have no perms")
        return   
    if len(args) == 0:
        await ctx.send("You must specify a module to load, idio.")
        return
    module = args[0]
    await loadModule(module, ctx)


@bot.command()
async def unloadmodule(ctx:botCommands.Context, *args):
    if ctx.message.author.guild_permissions.manage_guild == False:
        await ctx.send("You have no perms")
        return    
    if len(args) == 0:
        await ctx.send("You must specify a module to unload, idit.")
        return
    module = args[0]
    await unloadModule(module, ctx)

@bot.command()
async def reloadmodule(ctx:botCommands.Context, *args):
    if ctx.message.author.guild_permissions.manage_guild == False:
        await ctx.send("You have no perms")
        return
    if len(args) == 0:
        await ctx.send("You must specify a module to reload, idot.")
        return
    module = args[0]
    await unloadModule(module, ctx)
    await loadModule(module, ctx)

@bot.command()
async def update(ctx:botCommands.Context):
    if ctx.message.author.guild_permissions.manage_guild == False:
        await ctx.send("You have no perms")
        return
    await gitupdate()
    await ctx.reply("Pulled Changes")
    


bot.run(TOKEN)
