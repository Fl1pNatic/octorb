import discord
from discord.ext import commands

developer_ids = [
    404590613057503233,
    568050419251675176,
    426024775333314570,
    391234130387533825
]


class permissionErrors:
    class NonDeveloperError(commands.CheckFailure):
        pass


def devCheck(ctx):
    if isinstance(ctx, discord.Interaction):
        if ctx.user.id in developer_ids:
            return True
        return False
    else:
        if ctx.author.id in developer_ids:
            return True
        return False


class permissionChecks:
    def developer():
        async def predicate(ctx: discord.Interaction):
            if devCheck(ctx):
                return True
        return commands.check(predicate)
