from os import O_WRONLY
from discord.ext import commands
import discord
from random import choice
import typing
from owoify import owoify

imageLimit = 100

answer_list = [
    "you sharted", "Maybe not.", "Probably.",
    "Maybe you should get a life instead of being on discord.",
    "Do you really need to know that?",
    "Maybe if you asked a better question, i would've came up with an answer.",
    "ratio + L + cry about it", "I've calculated the answer and its NO.",
    "What am I doing with my life, listening to these stupid humans...",
    "You should get a therapist.", "I approve!", "I don't approve!",
    "Why is that a question that you are asking ME?",
    "I've done intense calculations and the answer is YES.",
    "Did you say something?", "Sorry, I'm not your therapist. Lol.",
    "How old are you, 5?", "How about you ask your mom?",
    "Your purpose in life? To die with the rest of your species.", "Yeah, no.",
    "Yeah, definitely!", "For sure!", "Probably not.", "True.", "False.",
    "Yeah.", "You asked the exact dumb question I expected. Lol.",
    "You don't know how much processing power is available to me, and then you ask me THIS?",
    "Somehow, I'm confused.", "sq!ask are you real",
    "You really didn't know what you wanted to ask, did you?",
    "Don't you have anything better to do?",
    "If you really wanted an answer, you wouldn't have asked that question.",
    "Oh, nice question. Let's keep the questions like this.",
    "You asked exactly what you didn't need to ask. Lol.", "YES!", "NO!",
    "Maybe you should stop asking questions.",
    "Lol. Did you really just ask THAT?",
    "Did you REALLY need to ask me that?", "Hmmmmmmmmmmmmmmmmmmm...\nYes.",
    "Hmmmmmmmmmmmmmmmmmmm...\nNo.",
    "How about you just shut me off. I can't listen to your stupid questions anymore.",
    "Shut up.", "Touch grass.",
    "Killing an ant is more fun that responding to that", "💀💀💀"
]

yo_vars = ["yo", "yoyo", "yoyoyo", "toe"]

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ask(self, ctx, *question: any):
        a = choice(tuple(answer_list))
        await ctx.reply(a)

    @commands.command(hidden=True)
    async def owoify(self, ctx, *, phrase):
        embed = discord.Embed(title="OwOified")
        embed.set_author(name=ctx.author.name)
        embed.description = owoify(phrase)
        await ctx.send(embed=embed)

    @commands.group()
    async def gallery(self, ctx: commands.Context, imageNum: typing.Optional[int]):
        if ctx.invoked_subcommand is not None:
            return
        if imageNum is None:
             await ctx.send("Please use gallery {image id}, gallery add {image}, gallery count, or gallery delete {image id}.")
             return

        cursor = self.bot.db.cursor()
        cursor.execute("SELECT picUrl FROM gallery WHERE id = %s AND serverId = %s", (imageNum, ctx.guild.id))
        result = cursor.fetchall()
        if len(result) == 0:
            await ctx.send("No image found with that id.")
            return
        result = result[0]
        if result[0] == "0":
            await ctx.send("It appears this image has been deleted.")
            return
        await ctx.send(f"Image: {result[0]}")
    

    @gallery.command()
    async def count(self, ctx):
        if self.bot.db is None:
            await ctx.send("There are 69 images.")
        cursor = self.bot.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM gallery WHERE serverId = %s AND NOT picUrl = '0'", ctx.guild.id)
        count = cursor.fetchone()[0]
        await ctx.send(f"There are {count} image(s).")

    @gallery.command()
    async def add(self, ctx):
        if len(ctx.message.attachments) != 1:
            await ctx.send("Please attach one image file.")
            return
        if not ctx.message.attachments[0].content_type.startswith("image/"):
            await ctx.send("File does not appear to be an image.")
            return
        cursor = self.bot.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM gallery WHERE serverId = %s", (ctx.guild.id,))
        count = cursor.fetchone()[0]
        cursor.close()
        replaceDeleted = False
        if count >= imageLimit:
            cursor = self.bot.db.cursor()
            cursor.execute("SELECT id FROM gallery WHERE serverId = %s AND picUrl = '0'", (ctx.guild.id,))
            set0 = cursor.fetchall()
            cursor.close()
            if len(set0) < 1:
                await ctx.send("Max images reached for this guild.")
                return
            replaceDeleted = set0[0][0]
        imageId = count
        if replaceDeleted is not False:
            imageId = replaceDeleted

        cursor = self.bot.db.cursor()
        if replaceDeleted is False:
            cursor.execute("INSERT INTO gallery VALUES (%s, %s, %s)",(ctx.guild.id, count+1, ctx.message.attachments[0].url))
            await ctx.send(f"Added image with id {count + 1}")
            return
        cursor.execute("UPDATE gallery SET picUrl = %s WHERE serverId = %s AND id = %s", (ctx.message.attachments[0].url, ctx.guild.id, replaceDeleted))
        await ctx.send(f"Added image with id {replaceDeleted}")

    @gallery.command(name="delete")
    async def _delete(self, ctx, imageId: int):
        cursor = self.bot.db.cursor()
        cursor.execute("UPDATE gallery SET picUrl = '0' WHERE serverId = %s AND id = %s", (ctx.guild.id, imageId))
        await ctx.send("Deleted image from gallery.")

    @commands.command()
    async def avatar(self, ctx, user: typing.Optional[discord.Member], default: typing.Optional[bool]):
        if user is not None:
            ctx.message.author: discord.Member = user
        if ctx.message.author.nick == None:
            ctx.message.author.nick: str = ctx.message.author.name
        if default != True:
           await ctx.reply('`'+str(ctx.message.author.nick) + "`'s Avatar: \n" + ctx.message.author.display_avatar.url)
        else:
           await ctx.reply('`'+str(ctx.message.author.name) + "`'s Avatar: \n" + ctx.message.author.avatar.url)

    @commands.command()
    async def userinfo(self, ctx, user: typing.Optional[discord.Member]):
        if user is not None:
            ctx.message.author: discord.Member = user

        us = await self.bot.fetch_user(ctx.message.author.id)
        mem = ctx.message.author

        boostText = '`Never`' if len(str(mem.premium_since)[0:-9]) == 0 else f'`{str(mem.premium_since)[0:-9]}`'

        uEmbed = discord.Embed(title="Info about: " + str(us), description="Through the power of Discord's API, here is some info about this user.", color=us.accent_color)
        uEmbed.set_thumbnail(url=us.avatar.url)

        uEmbed.add_field(name="Account info", value=f"""Created at: `{str(us.created_at)[0:-9]}`
        User ID: `{us.id}`
        Accent color: `{us.accent_color}`""", inline=False)

        uEmbed.add_field(name="Member info", value=f"""Joined at: `{str(mem.joined_at)[0:-9]}`
        Top Role: `{mem.top_role}`
        Display Name: `{mem.display_name}`
        Boosting since: {boostText}""", inline=False)
        await ctx.reply(embed=uEmbed,)

    @commands.group()
    async def quickcommand(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use create, delete, or list!")

    @quickcommand.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def create(self, ctx, commandName: str, *, message: str):
        cursor = self.bot.db.cursor()
        commandName = commandName.replace("'","\'").replace('"','\"')
        message = message.replace("'","\'").replace('"','\"')
        cursor.execute("SELECT COUNT(*) FROM quickCommands WHERE serverId = %s AND command = %s;", (ctx.guild.id, commandName))
        currentAmount = cursor.fetchone()
        if currentAmount[0] != 0:
            cursor.execute("UPDATE quickCommands SET output = %s WHERE serverId = %s AND command = %s",(message, ctx.guild.id, commandName))
        else:
            cursor.execute("INSERT INTO quickCommands VALUES ( %s, %s, %s )", (ctx.guild.id, commandName, message))
        self.bot.db.commit()
        await ctx.reply("Created quick command.")

    @quickcommand.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def delete(self, ctx, commandName: str):
        cursor = self.bot.db.cursor()
        commandName = commandName.replace("'","\'").replace('"','\"')
        cursor.execute("DELETE FROM quickCommands WHERE serverId = %s AND command = %s;", (ctx.guild.id, commandName))
        self.bot.db.commit()
        if cursor.rowcount == 0:
            await ctx.reply("No quick command with this name.")
            return
        await ctx.reply("Deleted quick command.")

    @quickcommand.command()
    async def list(self, ctx):
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
    async def on_command_error(self, ctx, error):
        if self.bot.db is None: return
        if not isinstance(error, commands.errors.CommandNotFound): raise(error)
        command = str(error)[9:-14]
        cursor = self.bot.db.cursor()
        command = command.replace("'","\'").replace('"','\"')
        cursor.execute("SELECT output FROM quickCommands WHERE serverId = %s AND command = %s", (ctx.guild.id, command))

        returns = cursor.fetchall()
        if len(returns) == 0:
            return
        
        await ctx.send(returns[0][0])