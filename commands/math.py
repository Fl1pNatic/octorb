import discord
from discord.ext import commands
import random
from py_expression_eval import Parser
from PermissionsChecks import permissionErrors, permissionChecks, devCheck

class math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.command()
    async def coinflip(self, ctx):
        result = random.choice(tuple([0, 1]))
        await ctx.reply("Heads" if result == 1 else "Tails")

    @commands.command()
    async def rng1000(self, ctx, min: int, max: int):
        if int(min) < -1000 or int(min) > 1000:
            await ctx.reply("Minimum number is too low or high")
            return
        if max < -1000 or max > 1000:
            await ctx.reply("Maximum number is too low or high")    
            return
        if max < min:
            await ctx.reply("Maximum number MUST be higher than minimum")
            return
        
        result = random.randrange(min, max)     
        await ctx.reply(result)

    @commands.command()
    @permissionChecks.developer()
    async def math(self, ctx, *, equation: str):
        mathPars = Parser()
        try:
            await ctx.reply(mathPars.parse(equation).evaluate({}))
        except:
            await ctx.reply("'"+equation+"' is not a valid expression")
            return              

    @bot.event
    async def on_command_error(ctx, error):
        match type(error):
            case permissionErrors.NonDeveloperError:
                await ctx.send("This command is limited to Octorb Developers.")
            case botCommands.errors.CommandInvokeError:
                if isinstance(error.original, discord.errors.HTTPException):
                    if error.original.code == 50035:
                        await ctx.send("it's too big daddy, it won't fit~")
            case _: raise(error)                