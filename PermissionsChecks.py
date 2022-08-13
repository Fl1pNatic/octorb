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

class permissionChecks:
    def developer():
        async def predicate(ctx: commands.Context):
            if ctx.author.id in developer_ids:
                return True
            raise permissionErrors.NonDeveloperError()
        return commands.check(predicate)

