import time
import typing

import discord
import typing
from discord.ext import tasks, commands
import string
from collections import Counter

maxXp = 14

cooldown = 60

ENGLISH_LETTER_FREQUENCIES = {
    'a': 0.0817, 'b': 0.0150, 'c': 0.0278, 'd': 0.0425, 'e': 0.1270, 'f': 0.0223,
    'g': 0.0202, 'h': 0.0609, 'i': 0.0697, 'j': 0.0015, 'k': 0.0077, 'l': 0.0403,
    'm': 0.0241, 'n': 0.0675, 'o': 0.0751, 'p': 0.0193, 'q': 0.0010, 'r': 0.0599,
    's': 0.0633, 't': 0.0906, 'u': 0.0276, 'v': 0.0098, 'w': 0.0236, 'x': 0.0015,
    'y': 0.0197, 'z': 0.0007
}

def english_score(text):
    og_counts = Counter(text)
    text = text.lower()
    text = ''.join(c for c in text if c.isascii())
    text = text.translate(str.maketrans('', '', string.punctuation + string.digits + string.whitespace))
    letter_counts = Counter(text)
    total_letters = sum(letter_counts.values())
    if total_letters == 0:
        return 0
    letter_frequencies = {letter: count / total_letters for letter, count in letter_counts.items()}
    score = sum(abs(letter_frequencies.get(letter, 0) - ENGLISH_LETTER_FREQUENCIES[letter])
                for letter in ENGLISH_LETTER_FREQUENCIES.keys())
    score /= len(og_counts)
    score = 1 - (score*10)
    return score if score > 0 else 0


class xp(commands.Cog):
    def user_in_server(self, USERID, SERVERID):
        print(USERID, SERVERID)
        return 0 if self.bot.get_guild(int(SERVERID)).get_member(int(USERID)) is None else 1
    def __init__(self, bot: commands.Bot) -> None:
        self.cooldowns = {}
        self.bot = bot
        self.messageCounts = {}
        self.db = bot.db
        self.clearCooldowns.start()
        self.db.create_function("USERINSERVER", 2, self.user_in_server)

    @tasks.loop(minutes=1)
    async def clearCooldowns(self):
        self.cooldowns = {key:val for key, val in self.cooldowns.items() if time.time() - val > cooldown}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        for prefix in (await self.bot.command_prefix(self.bot, message)):
            if message.content.startswith(prefix):
                return
        ## Check Cooldown
        if message.author.id in self.cooldowns:
            if time.time()-self.cooldowns[message.author.id] < cooldown:
                return
        self.cooldowns[message.author.id] = time.time()


        ## Frequency analysis, find xp amount and shit.
        await self.addUserXp(message.author.id, message.guild.id, int(english_score(message.content)*maxXp))


    async def addUserXp(self, memberId, serverId, xp):
        if self.db == None:
            return False
        if xp == 0:
            return True

        cursor = self.db.cursor()
        cursor.execute( "INSERT INTO xp (serverId, memberId, memberXp) VALUES (?, ?, ?) ON CONFLICT(serverId, memberId) DO UPDATE SET memberXp = memberXp + ?;", (serverId, memberId, xp, xp))
        self.db.commit()
        return True
        

    @commands.command(description="Shows a users xp")
    async def xp(self, ctx: commands.Context, user: typing.Optional[discord.Member]):
        """
        Parameters
        ------------
        user
            The user to get the xp of
        """
        if self.db == None:
            await ctx.send("You have 69 XP")
            return

        cursor = self.db.cursor()
        if user is not None:
            if not user.id in [member.id for member in ctx.guild.members]:
                user = ctx.author

        cursor.execute( "SELECT memberXp FROM xp WHERE serverId = ? and memberId = ?",
                        (ctx.guild.id, ctx.author.id))
        embed = discord.Embed(title="XP", color=0xda7dff)
        data = cursor.fetchone()
        if data is None:
            data = [0]
        embed.add_field(
            name=f"{ctx.author.display_name}", value=f"`XP: {data[0]}`")
        embed.set_thumbnail(url=str(ctx.author.display_avatar.url))
        await ctx.send(embed=embed)

    @commands.command(description="Shows the xp leaderboard.")
    async def xptop(self, interaction: commands.Context, page: typing.Optional[int]=1):
        cursor = self.db.cursor()
        cursor.execute( "SELECT memberXp, memberId FROM xp WHERE serverId = ? and USERINSERVER(memberId, serverId) = 1 ORDER BY memberXp DESC LIMIT ?,5", [
                       str(interaction.guild.id), (page-1)*5])
        embed = discord.Embed(title="XP Leaderboards", color=0xda7dff)
        embed.set_footer(text = f"Page: {+ page}")
        data = cursor.fetchall()
        if len(data) == 0:
            await interaction.send("Page has no data!")
            return
        for row in range(len(data)):
            embed.add_field(
                name=f"{(page-1)*5+1+row}.",
                value=f"<@{data[row][1]}>: `{data[row][0]}`", inline=False)
        await interaction.send(embed=embed)

    @commands.command(description="Gives the specified user xp.")
    @commands.has_guild_permissions(manage_messages=True)
    async def givexp(self, ctx: commands.Context, member: discord.Member, xp: int):
        """
        Parameters
        ------------
        user
            The user to give xp to.
        xp
            The amount of xp to give (can be negative)
        """
        if self.db is None:
            print("No db?")
            return
        if await self.addUserXp(member.id, ctx.guild_id, xp):
            await ctx.send(f"Gave {xp} xp to {member.display_name}.")
        else:
            await ctx.send("Failed to give member xp.")