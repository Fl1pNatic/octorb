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
    "Somehow, I'm confused.", "You really didn't know what you wanted to ask, did you?",
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

    @commands.hybrid_command(description="Lets you ask Octorb a question.")
    async def ask(self, ctx, question: str):
        a = choice(tuple(answer_list))
        await ctx.reply(a)

    @commands.hybrid_command(hidden=True, description="Owoifwies ywour text, because why nywot.")
    async def owoify(self, ctx:commands.Context, *, phrase:str):
        embed = discord.Embed(title="OwOified", color=0xda7dff)
        embed.set_author(name=ctx.message.author)
        embed.description = owoify(phrase)
        await ctx.reply(embed=embed)

    @commands.hybrid_group(description="Gallery commands.")
    async def gallery(self, ctx: commands.Context, image_num: typing.Optional[int]):
        if ctx.invoked_subcommand is not None:
            return
        if image_num is None:
             await ctx.reply("Please use gallery [media id], gallery add [media], gallery count, or gallery delete [media id].")
             return

        cursor = self.bot.db.cursor()
        cursor.execute("SELECT picUrl FROM gallery WHERE id = %s AND serverId = %s", (image_num, ctx.guild.id))
        result = cursor.fetchall()
        if len(result) == 0:
            await ctx.reply("No media found with that id.")
            return
        result = result[0]
        if result[0] == "0":
            await ctx.reply("It appears this content has been deleted.")
            return
        await ctx.reply(f"{result[0]}")
    

    @gallery.command(description="Gets the number of images in the server's gallery.")
    async def count(self, ctx:commands.Context):
        if self.bot.db is None:
            await ctx.reply("There are 69 images.")
        cursor = self.bot.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM gallery WHERE serverId = %s AND NOT picUrl = '0'", ctx.guild.id)
        count = cursor.fetchone()[0]
        await ctx.reply(f"There are {count} stored.")

    @gallery.command(description="Adds the media to the gallery.")
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def add(self, ctx:commands.Context):
        if len(ctx.message.attachments) != 1:
            await ctx.reply("Please attach one image/video file.")
            return
        if not ctx.message.attachments[0].content_type.startswith("image/"):
            if not ctx.message.attachments[0].content_type.startswith("video/"):
                await ctx.reply("File does not appear to be an image/video.")
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
                await ctx.reply("Max content amount reached for this guild.")
                return
            replaceDeleted = set0[0][0]
        imageId = count
        if replaceDeleted is not False:
            imageId = replaceDeleted

        cursor = self.bot.db.cursor()
        if replaceDeleted is False:
            cursor.execute("INSERT INTO gallery VALUES (%s, %s, %s)",(ctx.guild.id, count+1, ctx.message.attachments[0].url))
            await ctx.reply(f"Added media with id {count + 1}")
            return
        cursor.execute("UPDATE gallery SET picUrl = %s WHERE serverId = %s AND id = %s", (ctx.message.attachments[0].url, ctx.guild.id, replaceDeleted))
        await ctx.reply(f"Added media with id {replaceDeleted}")

    @gallery.command(name="delete", description="Deletes the image from the gallery.")
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def _delete(self, ctx:commands.Context, image_id: int):
        cursor = self.bot.db.cursor()
        cursor.execute("UPDATE gallery SET picUrl = '0' WHERE serverId = %s AND id = %s", (ctx.guild.id, image_id))
        await ctx.reply("Deleted content from gallery.")

    @commands.hybrid_command(description="Gets the users server or default avatar.")
    async def avatar(self, ctx:commands.Context, user: typing.Optional[discord.Member], default: typing.Optional[bool]):
        if user is not None:
            ctx.message.author: discord.Member = user
        avEmbed = discord.Embed(color=0xda7dff)
        if ctx.message.author.nick == None:
            ctx.message.author.nick: str = ctx.message.author.name
        if default != True:
            avEmbed.title = ctx.message.author.nick + "'s avatar"
            avEmbed.set_image(url=ctx.message.author.display_avatar.url)
        else:
            avEmbed.title = ctx.message.author.name + "'s default avatar"
            avEmbed.set_image(url=ctx.message.author.avatar.url)
        await ctx.reply(embed=avEmbed)

    @commands.hybrid_command(description="Shows some information about the user.")
    async def userinfo(self, ctx:commands.Context, user: typing.Optional[discord.Member]):
        if user is not None:
            ctx.message.author: discord.Member = user

        us = await self.bot.fetch_user(ctx.message.author.id)
        mem = ctx.message.author

        boostText = '`Never`' if len(str(mem.premium_since)[0:-9]) == 0 else f'`{str(mem.premium_since)[0:-9]}`'

        uEmbed = discord.Embed(title="Info about: " + str(us), description="Through the power of Discord's API, here is some info about this user.", color=us.accent_color)
        uEmbed.set_thumbnail(url=us.display_avatar.url)

        uEmbed.add_field(name="Account info", value=f"""Created at: `{str(us.created_at)[0:-9]}`
        User ID: `{us.id}`
        Accent color: `{us.accent_color}`
        Bot: `{"Yes" if us.bot else "No" }`""", inline=False)

        uEmbed.add_field(name="Member info", value=f"""Joined at: `{str(mem.joined_at)[0:-9]}`
        Top Role: `{mem.top_role}`
        Display Name: `{mem.display_name}`
        Boosting since: {boostText}""", inline=False)
        await ctx.reply(embed=uEmbed,)
