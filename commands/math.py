import random
import typing

import discord
from discord.ext import commands
import aiohttp
import json


class math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Heads or tails, what'll it be?")
    async def coinflip(self, ctx: commands.Context):
        result = random.choice(tuple([0, 1]))
        await ctx.send("Heads" if result == 1 else "Tails")

    @commands.command(description="Gives you a random number. (Default: 0 - 10)")
    async def rng(self, ctx: commands.Context, min: typing.Optional[int]=0, max: typing.Optional[int]=10):
        """
        Parameters
        ------------
        min
            The lowest possible number
        max
            The highest possible number
        """
        if max == min:
            await ctx.send(min)
            return

        if max < min:
            max, min = (min, max)

        result = random.randrange(min, max)
        await ctx.send(result)

    @commands.command(description="Gets the result of the given math equation.")
    async def math(self, ctx: commands.Context, *, equation: str):
        async with aiohttp.ClientSession() as session:
            try:
                e = await (await session.post(
                f'http://api.mathjs.org/v4/', data=json.dumps({"expr":equation.splitlines()}), headers={'content-type': 'application/json'})).json()
                if e['result'] == None:
                    await ctx.reply(embed=discord.Embed(title="Error in math equation!").add_field(name="Error",value=e['error']))
                else:
                    await ctx.reply(embed=discord.Embed(title="Math Evaluation").add_field(name="Equation"+("s" if len(equation.splitlines()) > 1 else ""), value=equation, inline=False).add_field(name="Result"+("s" if len(e['result']) > 1 else ""), value="\n".join(e['result'])))
            except:
                await ctx.reply("Error fetching result!")


async def setup(bot):
    await bot.add_cog(math(bot))