import sys
import traceback
import re
import discord
from discord.ext import commands
from dotenv import dotenv_values, load_dotenv
import sqlite3
from PermissionsChecks import permissionErrors
import PermissionsChecks
import datetime
import aiohttp
import editdistance

sys.path.append(".")

load_dotenv()
TOKEN = dotenv_values()["TOKEN"]

async def determine_prefix(bot, message: discord.Message):
    if bot.devmode:
        return [bot.user.mention + " "]
    return ["!","oc!","o!"]
    
db = sqlite3.connect("database.db")

devmode = "DEVMODE" in dotenv_values()

cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS `gallery` (
  `serverId` tinytext,
  `id` int DEFAULT NULL,
  `picUrl` tinytext
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS `quickCommands` (
  `serverId` tinytext,
  `command` tinytext,
  `output` text
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS `xp` (
  `serverId` VARCHAR(25),
  `memberId` VARCHAR(25),
  `memberXp` int DEFAULT NULL,
  PRIMARY KEY (serverId, memberId)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS `xpRewards` (
  `serverId` VARCHAR(25),
  `roleId` VARCHAR(25),
  `roleXp` int DEFAULT NULL,
  PRIMARY KEY (serverId, roleId)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS `serverNotifications` (
  `serverId` VARCHAR(25),
  `channelId` VARCHAR(25),
  `sendNotifs` INTEGER,
  PRIMARY KEY (serverId)
)
""")

async def devCheck(ctx: commands.Context):
    if PermissionsChecks.devCheck(ctx):
        return True


class Octorb(commands.Bot):
    def __init__(self, db, devmode):
        super().__init__(command_prefix=determine_prefix,
                      activity=discord.Activity(
                      type=discord.ActivityType.watching, name="!help for commands", url="https://github.com/x8c8r/octorb", start=datetime.datetime.now()),
                      intents=discord.Intents.all(),
                      help_command=None,
                      case_insensitive=True)
        self.db = db
        self.devmode = devmode
        if self.devmode:
            self.add_check(devCheck)

    async def setup_hook(self):
        await self.load_extension("commands.fun")
        await self.load_extension("commands.xp")
        await self.load_extension("commands.other")
        await self.load_extension("commands.moderation")
        await self.load_extension("commands.math")
        await self.load_extension("commands.developer")
        await self.load_extension("commands.dynamic")
        
        
        self.logging_session = aiohttp.ClientSession()
        webhook_url = dotenv_values()["logger_webhook"]
        self.logging_hook = discord.Webhook.from_url(webhook_url, session=self.logging_session)

        self.log_upload_session = aiohttp.ClientSession()
        self.log_upload_session.headers.update({"Authorization": f"Bearer {dotenv_values()['HASTEBIN_API_KEY']}","content-type": "text/json"})

        print(f"It's {self.user.name}in' time")
        if db is None:
            print(f"WARNING: BOT IS NOT CONNECT TO A DATABASE. SOME COMMANDS MAY NOT WORK.")

    async def on_disconnect():  
        print("Disconnected from Discord")

    async def on_message(self, message: discord.Message):
        if not PermissionsChecks.devCheck(message):
            if message.guild == None:
                if message.author.bot:
                    return
                await message.channel.send("You are not allowed to use the bot in DMs")
                return
        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error):
        match error:
            case permissionErrors.NonDeveloperError():
                await ctx.reply("This command is limited to Octorb Developers.")
            case commands.errors.MissingRequiredArgument():
                await ctx.reply(f"Missing argument: {error.param.name.capitalize()}")
            case commands.errors.MissingRequiredAttachment():
                await ctx.reply(f"Missing attachement.")
            case commands.CommandInvokeError(original=discord.HTTPException(code=50035)):
                    await ctx.reply("Command output too large.")
            case commands.errors.MissingPermissions():
                perms = error.missing_permissions
                await ctx.reply(f"You are missing the following permissions needed to use this command: {' '.join(str(x).replace('_', ' ').capitalize() for x in perms)}")
            case commands.errors.CommandNotFound():
                closestCommand = (2, None)
                for command in self.commands:
                    dist = editdistance.eval(command.name, ctx.invoked_with)
                    if dist < closestCommand[0]:
                        closestCommand = (dist, command.name)
                if closestCommand[1] is not None and ctx.message.author.bot is not True:
                    await ctx.reply(f"That command does not exist. Maybe you meant {ctx.prefix}{closestCommand[1]}?")
            case commands.errors.NoPrivateMessage():
                await ctx.reply("This command cannot be used in dms.")
            case commands.errors.BadArgument():
                await ctx.reply("Argument is an incorrect type.")
            case commands.errors.BadLiteralArgument():
                await ctx.reply(f"Parameter `{error.param.name}` must be one of " + ' '.join([f"`{option}`" for option in error.literals]))
            case commands.errors.CheckFailure():
                await ctx.reply("You can't run this command.")
            case commands.errors.CommandOnCooldown():
                await ctx.reply(f"You can't use this command for {round(error.retry_after,1)} seconds.")
            case _:
                etype = type(error)
                trace = error.__traceback__

                lines = traceback.format_exception(etype, error, trace)
                traceback_text = ''.join(lines)

                log_upload = await self.log_upload_session.post("https://hastebin.com/documents", data=f"Message Info: {ctx.message}\n\nCommand: {ctx.message.content}\n\nTraceback: {traceback_text}")
                content = await log_upload.json()
                if(log_upload.status != 200):
                    print(f"Error! Logging the error returned status {log_upload.status}")
                    print(content["message"])
                    return

                await self.logging_hook.send(
                    ' '.join([f"<@{id}>" for id in PermissionsChecks.developer_ids] if self.devmode == False else 'Error'),
                    embed=discord.Embed(title="ERROR", description="An error occurred!")
                        .add_field(name="Error Type:", value=etype.__name__, inline=False)
                        .add_field(name="Traceback:", value=f"https://hastebin.com/share/{content['key']}")
                        )
                await ctx.send("We ran into an unknown problem, and we're working on it.")


    async def botperms_check(ctx: commands.Context):
        guild = ctx.guild
        me = guild.me if guild is not None else ctx.bot.user
        permissions = ctx.channel.permissions_for(me)

        if getattr(permissions, "send_messages") is False:
            raise commands.BotMissingPermissions(["send_messages"])
        return True


bot = Octorb(db, devmode)
bot.run(TOKEN)
