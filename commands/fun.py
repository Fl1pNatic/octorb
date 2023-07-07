import typing
from os import O_WRONLY
from random import choice
import aiohttp
import discord
from discord.ext import commands
from owoify import owoify
from owoify import Owoness

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
    "Did you REALLY need to ask me that?", "Hmmmmmmmmmmmmmmmmmmm...\n||Yes.||",
    "Hmmmmmmmmmmmmmmmmmmm...\n||No.||",
    "How about you just shut me off. I can't listen to your stupid questions anymore.",
    "Shut up.", "Touch grass.",
    "Killing an ant is more fun that responding to that", "💀💀💀"
]

yo_vars = ["yo", "yoyo", "yoyoyo", "toe"]


class fun(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command(description="Ask Octorb a question")
    async def ask(self, ctx: commands.Context, question: str):
        """
        Parameters
        ------------
        question
            The question you're asking.
        """
        a = choice(tuple(answer_list))
        await ctx.send(a)

    @commands.command(description="Owoifwies ywour text, because why nywot")
    async def owoify(self, ctx: commands.Context, *, phrase: str):
        """
        Parameters
        ------------
        phrase
            Teh thing u want Owoifwied :3
        """
        embed = discord.Embed(title="OwOified", color=0xda7dff)
        embed.set_author(name=ctx.author)
        embed.description = owoify(phrase, level=Owoness.Uvu)
        await ctx.send(embed=embed)

    @commands.command(description="Gets user's server or default avatar.")
    async def avatar(self, ctx: commands.Context, user: typing.Optional[discord.Member], default: typing.Optional[bool]):
        """
        Parameters
        ------------
        user
            The user to get the avatar of
        default
            Whether to get user's account avatar [true] or server avatar [false (Default)]
        """
        if user is not None:
            ctx.author: discord.Member = user
        avEmbed = discord.Embed(color=0xda7dff)
        if ctx.author.nick == None:
            ctx.author.nick: str = ctx.author.name
        if default != True:
            avEmbed.title = ctx.author.nick + "'s avatar"
            avEmbed.set_image(url=ctx.author.display_avatar.url)
        else:
            avEmbed.title = ctx.author.name + "'s default avatar"
            avEmbed.set_image(url=ctx.author.avatar.url)
        await ctx.send(embed=avEmbed)

    @commands.command(description="Gets the definition for a word.")
    async def define(self, ctx: commands.Context, *, word: str):
        async with aiohttp.ClientSession() as session:
            e = await (await session.get(
            f'https://api.urbandictionary.com/v0/define?term={word.capitalize()}')).json()
            if len(e['list']) < 1:
                await ctx.send("Definition not found.")
                return
            await ctx.send(embed=discord.Embed(color=0xda7dff, title=f"Definition of {word}", description=e['list'][0]['definition']))

    @commands.command(description="Shows some information about the user.")
    async def userinfo(self, ctx: commands.Context, user: typing.Optional[discord.Member]):
        """
        Parameters
        ------------
        user
            The user to get info about
        """
        if user is not None:
            ctx.author: discord.Member = user

        us = await self.bot.fetch_user(ctx.author.id)
        mem = ctx.author

        userTag = "@" + us.name if us.discriminator == "0" else us.name + "#" + us.discriminator

        boostText = '`Never`' if len(str(mem.premium_since)[
                                     0:-9]) == 0 else f'`{str(mem.premium_since)[0:-9]}`'

        uEmbed = discord.Embed(title="Info about: " + str(
            userTag), description="Through the power of Discord's API, here is some info about this user.", color=us.accent_color)
        uEmbed.set_thumbnail(url=us.display_avatar.url)

        uEmbed.add_field(name="Account info", value=f"""Created at: `{str(us.created_at)[0:-9]}`
        User ID: `{us.id}`
        Accent color: `{us.accent_color if us.accent_color is not None else "Not set"}`
        Bot: `{"Yes" if us.bot else "No" }`""", inline=False)

        uEmbed.add_field(name="Member info", value=f"""Joined at: `{str(mem.joined_at)[0:-9]}`
        Top Role: `{mem.top_role}`
        Display Name: `{mem.display_name}`
        Boosting since: {boostText}""", inline=False)

        await ctx.send(embed=uEmbed,)
async def setup(bot):
    await bot.add_cog(fun(bot))