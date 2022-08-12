import discord
from discord.ext import commands
import random
from py_expression_eval import Parser

class math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.command()
    async def coinflip(self, ctx):
        result = random.choice(tuple([0, 1]))
        await ctx.reply("Heads" if result == 1 else "Tails")

    @commands.command()
    async def rng1000(self, ctx, *args):
        if len(args) < 2:
            await ctx.reply("Input minimum and maximum number (In range of -1000 to 1000)")
            return

        min = args[0]
        max = args[1]
        if isinstance(int(min), int) == False or isinstance(int(max), int) == False:
            await ctx.reply("You have to input numbers")
            return

        min = int(min)
        max = int(max)
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
    async def math(self, ctx, *, eq=None):
        mathPars = Parser()
        if eq==None:
            await ctx.reply("Input a math expression")
            return
        try:
            await ctx.reply(mathPars.parse(eq).evaluate({}))
        except:
            await ctx.reply("'"+eq+"' is not a valid expression")
            return              