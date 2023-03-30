import discord
from discord.ext import commands

developer_ids = [
    404590613057503233,
    426024775333314570,
    391234130387533825
]

blocked_ids = [
    568050419251675176
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

def blockedCheck(ctx):
    if isinstance(ctx, discord.Interaction):
        if ctx.user.id in blocked_ids:
            return False
        return True
    else:
        if ctx.author.id in blocked_ids:
            return False
        return True


class permissionChecks:
    def developer():
        async def predicate(ctx: discord.Interaction):
            if devCheck(ctx):
                return True
        return commands.check(predicate)
