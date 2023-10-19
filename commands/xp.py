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
        await self.addUserXp(message.author.id, message.guild.id, int(english_score(message.content)*maxXp), message.channel)


    async def addUserXp(self, memberId, serverId, xp, channel):
        if self.db == None:
            return False
        if xp == 0:
            return True

        cursor = self.db.cursor()
        cursor.execute( "INSERT INTO xp (serverId, memberId, memberXp) VALUES (?, ?, ?) ON CONFLICT(serverId, memberId) DO UPDATE SET memberXp = memberXp + ?;", (serverId, memberId, xp, xp))
        self.db.commit()
        cursor.execute(" SELECT memberXp FROM xp WHERE serverId = ? AND memberId = ?", (serverId, memberId))
        newXp = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM xpRewards WHERE serverId = ? AND ? >= roleXp AND ? < roleXp", (serverId, newXp, newXp-xp))
        roles = cursor.fetchall()
        if len(roles) < 1:
            return True

        await channel.guild.get_member(memberId).add_roles(*[channel.guild.get_role(int(id[1])) for id in roles])

        if len(roles) > 1:
            rewardsEmbed = discord.Embed(title="XP Rewards!", description=f"<@{memberId}> just got the following rewards:\n", color=0xda7dff)
            for role in roles:
                rewardsEmbed.description += f"\n<@&{role[1]}> for {role[2]} xp."
            await channel.send(embed=rewardsEmbed)
        
        else: await channel.send(embed=discord.Embed(title="XP Reward!", description=f"<@{memberId}> just gained the <@&{roles[0][1]}> role for {roles[0][2]} xp!", color=0xda7dff))

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
        if user is None or not user.id in [member.id for member in ctx.guild.members]:
            user = ctx.author
        cursor.execute( "SELECT memberXp, (SELECT COUNT(*)+1 FROM xp AS x WHERE x.serverId = xp.serverId AND x.memberXp > xp.memberXp AND USERINSERVER(x.memberId, x.serverId) = 1) AS position FROM xp WHERE serverId = ? AND memberId = ?",
                        (ctx.guild.id, user.id))
        embed = discord.Embed(title="XP", color=0xda7dff)
        data = cursor.fetchall()
        if len(data) is 0:
            await ctx.reply(f"No xp data for that user!")
            return
        data = data[0]
        cursor.execute("SELECT roleId, roleXp FROM xpRewards WHERE serverId = ? AND roleXp > ? ORDER BY roleXp ASC LIMIT 1;", (ctx.guild.id, data[0]))

        nextRole = cursor.fetchone()

        embed.add_field(
            name=f"{user.display_name}", value=f"`XP: {data[0]}`\n`Position: {data[1]} of {len(ctx.guild.members)}`\n {f'`{nextRole[1]-data[0]} xp to` <@&{nextRole[0]}>' if nextRole is not None else 'No more xp rewards.'}")
        embed.set_thumbnail(url=str(user.display_avatar.url))
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
        if await self.addUserXp(member.id, ctx.guild.id, xp, ctx.channel):
            await ctx.send(f"Gave {xp} xp to {member.display_name}.")
        else:
            await ctx.send("Failed to give member xp.")
    
    @commands.command(description="Clears specified user's xp data.")
    @commands.has_guild_permissions(manage_messages=True)
    async def clearxp(self, ctx: commands.Context, user: discord.Member):
        """
        Parameters
        ------------
        user
            The user to clear xp data of.
        """
        if self.db is None:
            print("No db?")
            return
        cursor = self.db.cursor()
        if user is None or not user.id in [member.id for member in ctx.guild.members]:
            await ctx.reply("No user specified!")
        cursor.execute( "DELETE FROM xp WHERE serverId = ? and memberId = ?;",
                        (ctx.guild.id, user.id))
        await ctx.reply(f"Deleted XP data of {user.name}." )

    @commands.group(description="Xp Rewards")
    @commands.guild_only()
    async def rewards(self, ctx: commands.Context):
        """
        Use to list xp rewards, or use subcommands add and remove to create xp rewards
        """
        if ctx.invoked_subcommand is not None:
            return
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM xpRewards WHERE serverId = ?", (ctx.guild.id, ))
        embed = discord.Embed(title="Xp Rewards")
        for reward in cursor:
            embed.add_field(value=f"<@&{reward[1]}>", name=f"{reward[2]} xp", inline=False)
        if len(embed.fields) < 1:
            await ctx.reply("No rewards for this server.")
            return
        await ctx.reply(embed=embed)

    @rewards.command(description="Creates an XP Reward")
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, xp: int, role: discord.Role):
        """
        Parameters
        ------------
        xp
            The amount of xp to reward the role at.
        role
            The role to be rewarded.
        """
        if role >= ctx.guild.get_member(ctx.bot.user.id).top_role or role >= ctx.author.top_role:
            await ctx.reply("Role too high!")
            return
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(roleId) FROM xpRewards WHERE serverId = ?", (ctx.guild.id, ))
        e = cursor.fetchone()[0]
        if e >= 25:
            await ctx.reply("You can only have 25 role rewards.")
            return
        cursor.execute("INSERT INTO xpRewards (serverId, roleId, roleXp) VALUES (?, ?, ?) ON CONFLICT(serverId, roleId) DO UPDATE SET roleXp = ?;", (ctx.guild.id, role.id, xp, xp))
        await ctx.reply("Set XP Reward!")

    @rewards.command(description="Deletes an XP Reward")
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, role: discord.Role):
        if role >= ctx.guild.get_member(ctx.bot.user.id).top_role or role >= ctx.author.top_role:
            await ctx.reply("Role too high!")
            return
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM xpRewards WHERE serverId = ? AND roleId = ?", (ctx.guild.id, role.id))
        await ctx.reply("Deleted xp reward.\n`Note: This does not remove the role from users who had already gained it.`")

async def setup(bot):
    await bot.add_cog(xp(bot))