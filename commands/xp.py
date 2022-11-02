import asyncio
import typing
from math import log

import discord
import typing
from discord.ext import commands, tasks

xp = {}


class xp(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.messageCounts = {}
        self.db = bot.db

    async def cog_load(self):
        self.processXP.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        for prefix in (self.bot.command_prefix):
            if message.content.startswith(prefix):
                return
        if not message.guild.id in self.messageCounts:
            self.messageCounts[message.guild.id] = {}

        if not message.author.id in self.messageCounts[message.guild.id]:
            self.messageCounts[message.guild.id][message.author.id] = 1
            return
        self.messageCounts[message.guild.id][message.author.id] += 1

    @tasks.loop(minutes=1)
    async def processXP(self):
        await self.calcXP()
        await asyncio.sleep(60)

    async def calcXP(self):
        xpStores = []
        for s in self.messageCounts.keys():
            for u in self.messageCounts[s].keys():
                uX = round(log(self.messageCounts[s][u])+5, 0)
                xpStores.append({"server": s, "user": u, "xp": uX})
        await self.storeXP(xpStores)
        self.messageCounts = {}

    async def storeXP(self, xpStore):
        if self.db is None:
            # print(xpStore)
            return
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM xp")
        results = cursor.fetchall()
        members = {}
        for result in results:
            if result[0] not in members:
                members[result[0]] = {}
            members[result[0]][result[1]] = result[2]
            # members = {
            #       guildId: {
            #           memberId: xp
            #       }
            #   }
        changedData = []
        newData = []
        for userdata in xpStore:
            server = str(userdata["server"])
            user = str(userdata["user"])
            xp = int(userdata["xp"])
            if server in members.keys():
                if user in members[server].keys():
                    changedData.append(
                        (server, user, xp+members[server][user]))
                    continue
            newData.append((server, user, xp))

        updateCommand = "UPDATE xp SET memberXp = %s WHERE serverId = %s AND memberId = %s"
        createCommand = "INSERT INTO xp (serverId, memberId, memberXp) VALUES (%s, %s, %s)"

        for user in changedData:
            cursor.execute(updateCommand, (user[2], user[0], user[1]))
        for user in newData:
            cursor.execute(createCommand, (user[0], user[1], user[2]))

        self.db.commit()

    @commands.hybrid_command(description="Shows a users xp")
    async def xp(self, ctx: commands.Context, user: typing.Optional[discord.Member]):
        """
        Parameters
        ------------
        user
            The user to get the xp of.
        """
        if self.db == None:
            await ctx.reply("You have 69 XP")
            return

        cursor = self.db.cursor()
        if user is not None:
            if not user.id in [member.id for member in ctx.guild.members]:
                user = ctx.message.author

        try:
            cursor.execute("SELECT memberXp FROM xp WHERE serverId = %s and memberId = %s",
                           (ctx.message.guild.id, ctx.message.author.id))
            embed = discord.Embed(title="XP", color=0xda7dff)
            embed.add_field(
                name=f"{ctx.message.author.display_name}", value=f"`XP: {cursor.fetchone()[0]}`")
            embed.set_thumbnail(url=str(ctx.message.author.display_avatar.url))
            await ctx.reply(embed=embed)
            return
        except (Exception) as e:
            await ctx.reply("You don't have any XP")
            await ctx.reply(f"{e}")
            return

    @commands.hybrid_command(description="Shows the xp leaderboard.")
    async def xptop(self, ctx: commands.Context, page: typing.Optional[int]):
        if self.db == None:
            await ctx.reply("Squidward")
            return

        if page is None:
            page = 1
        cursor = self.db.cursor()
        cursor.execute("SELECT memberXp, memberId FROM xp WHERE serverId = %s ORDER BY memberXp DESC", [
                       str(ctx.message.guild.id)])
        embed = discord.Embed(title="XP Leaderboards", color=0xda7dff)
        data = cursor.fetchall()
        for i in range(min(len(data), 5 * page) + (page - 1)):
            embed.add_field(
                name=f"{i + 1}.", value=f"<@{data[i][1]}>: `{data[i][0]}`", inline=False)

        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Gives the specified user xp.")
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
        await self.storeXP([{"server": ctx.guild.id, "user": member.id, "xp": xp}])
        await ctx.reply(f"Gave {xp} xp to {member.display_name}.")
