import discord
from discord.ext import commands
import random
from py_expression_eval import Parser

class math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.command()
    @commands.bot_has_permissions
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
    async def math(self, ctx, *, equation):
        mathPars = Parser()
        if eq==None:
            await ctx.reply("Input a math expression")
            return
        try:
            await ctx.reply(mathPars.parse(equation).evaluate({}))
        except:
            await ctx.reply("'"+equation+"' is not a valid expression")
            return              