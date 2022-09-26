import discord
from discord.ext import commands
import random
from py_expression_eval import Parser
import typing
from PermissionsChecks import permissionErrors, permissionChecks, devCheck
# from .. import PermissionsChecks

class math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.hybrid_command()
    async def coinflip(self, ctx:commands.Context):
        result = random.choice(tuple([0, 1]))
        await ctx.reply("Heads" if result == 1 else "Tails")

    @commands.hybrid_command()
    async def rng(self, ctx:commands.Context, min: typing.Optional[int], max: typing.Optional[int]):
        if max is None:
            if min is None:
                max = 10
                min = 0
            else:
                max = min
                min = 0

        if max == min: 
            await ctx.reply(min)
            return

        if max < min: max, min = (min, max)


        result = random.randrange(min, max)     
        await ctx.reply(result)

    # @commands.command()
    # @permissionChecks.developer()
    async def math(self, ctx:commands.Context, *, equation: str):
        mathPars = Parser()
        try:
            await ctx.reply(mathPars.parse(equation).evaluate({}))
        except:
            await ctx.reply("'"+equation+"' is not a valid expression")
            return                       