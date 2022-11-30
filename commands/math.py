import random
import typing

import discord
from discord import app_commands
from discord.ext import commands


class math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Heads or tails, what'll it be?")
    async def coinflip(self, ctx: discord.Interaction):
        result = random.choice(tuple([0, 1]))
        await ctx.response.send_message("Heads" if result == 1 else "Tails")

    @app_commands.command(description="Gives you a random number. (Default: 0 - 10)")
    async def rng(self, ctx: discord.Interaction, min: typing.Optional[int]=0, max: typing.Optional[int]=10):
        """
        Parameters
        ------------
        min
            The lowest possible number
        max
            The highest possible number
        """
        if max == min:
            await ctx.response.send_message(min)
            return

        if max < min:
            max, min = (min, max)

        result = random.randrange(min, max)
        await ctx.response.send_message(result)
