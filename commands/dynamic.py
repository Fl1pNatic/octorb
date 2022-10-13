from discord.ext import commands
import discord

class dynamic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_group(description="Commands for quick commands.")
    async def quickcommand(self, ctx:commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply("Use create, delete, or list!")

    @quickcommand.command(description="Creates a quick command.")
    @commands.has_guild_permissions(manage_messages=True)
    async def create(self, ctx:commands.Context, command_name: str, *, message: str):
        cursor = self.bot.db.cursor()
        command_name = command_name.replace("'","\'").replace('"','\"')
        message = message.replace("'","\'").replace('"','\"')
        cursor.execute("SELECT COUNT(*) FROM quickCommands WHERE serverId = %s AND command = %s;", (ctx.guild.id, command_name))
        currentAmount = cursor.fetchone()
        if currentAmount[0] != 0:
            cursor.execute("UPDATE quickCommands SET output = %s WHERE serverId = %s AND command = %s",(message, ctx.guild.id, command_name))
        else:
            cursor.execute("INSERT INTO quickCommands VALUES ( %s, %s, %s )", (ctx.guild.id, command_name, message))
        self.bot.db.commit()
        await ctx.reply("Created quick command.")

    @quickcommand.command(description="Deletes a quick command.")
    @commands.has_guild_permissions(manage_messages=True)
    async def delete(self, ctx:commands.Context, command_name: str):
        cursor = self.bot.db.cursor()
        command_name = command_name.replace("'","\'").replace('"','\"')
        cursor.execute("DELETE FROM quickCommands WHERE serverId = %s AND command = %s;", (ctx.guild.id, command_name))
        self.bot.db.commit()
        if cursor.rowcount == 0:
            await ctx.reply("No quick command with this name.")
            return
        await ctx.reply("Deleted quick command.")

    @quickcommand.command(description="Lists all the server's quickcommands.")
    async def list(self, ctx:commands.Context):
        cursor = self.bot.db.cursor()
        cursor.execute("SELECT command FROM quickCommands WHERE serverId = %s", (ctx.guild.id,))
        embed = discord.Embed(
            title="Quick commands list.",
            color=0xff00bb,
            description="Use like any other command! Use `sq!quickcommand create` to create and `sq!quickcommand delete` to delete."
        )
        commands = cursor.fetchall()
        cL = ""
        for command in commands:
            cL = cL + command[0] + ", "
        cL = cL[0:-2]
        embed.add_field(name="List", value=cL, inline=True)
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error:Exception):
        if self.bot.db is None: return
        if not isinstance(error, commands.errors.CommandNotFound): raise(error)
        command = str(error)[9:-14]
        cursor = self.bot.db.cursor()
        command = command.replace("'","\'").replace('"','\"')
        cursor.execute("SELECT output FROM quickCommands WHERE serverId = %s AND command = %s", (ctx.guild.id, command))

        returns = cursor.fetchall()
        if len(returns) == 0:
            return
        
        await ctx.reply(returns[0][0])