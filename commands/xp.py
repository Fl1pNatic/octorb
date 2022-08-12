from email import message
from math import log
from concurrent.futures import process
import random
from readline import replace_history_item
import nextcord
from nextcord.ext import commands
import asyncio
import typing
import mysql.connector
xp = {}

class xp(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.messageCounts = {}
        self.db:mysql.connector.MySQLConnection = bot.db

    @commands.Cog.listener()
    async def on_ready(self):
        await self.processXP()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # print(self.messageCounts)
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


    async def processXP(self):
        while True:
            await self.calcXP()
            await asyncio.sleep(60)

    async def calcXP(self):
        xpStores = []
        for s in self.messageCounts.keys():
            for u in self.messageCounts[s].keys():
                uX = round(log(self.messageCounts[s][u])+5,0)
                xpStores.append({"server":s,"user":u,"xp":uX})
        await self.storeXP(xpStores)
        self.messageCounts = {}

    async def storeXP(self, xpStore):
        if self.db is None:
            print(xpStore)
            return
        cursor:mysql.connector.connection.MySQLCursor = self.db.cursor()
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
                    changedData.append((server, user, xp+members[server][user]))
                    continue
            newData.append((server, user, xp))
        
        updateCommand = "UPDATE xp SET memberXp = %s WHERE serverId = %s AND memberId = %s"
        createCommand = "INSERT INTO xp (serverId, memberId, memberXp) VALUES (%s, %s, %s)"

        for user in changedData:
            cursor.execute(updateCommand, (user[2], user[0], user[1]))
        for user in newData:
            cursor.execute(createCommand, (user[0],user[1],user[2]))

        self.db.commit()
        print(cursor.rowcount)
        
    @commands.command()
    async def xp(self, ctx, user: typing.Optional[str]):
        if self.db == None:
            await ctx.reply("You have 69 XP")
            return
        
        cursor:mysql.connector.connection.MySQLCursor = self.db.cursor()
        if user is not None:
            if(user.startswith("<@")):
                user = user[2:len(user)-1]
            print(user)
            try:
                user = int(user)
                ctx.message.author: nextcord.Member = ctx.message.guild.get_member(user)
            except(Exception) as e:
                await ctx.send("Invalid user")
                return
        try:
            cursor.execute("SELECT memberXp FROM xp WHERE serverId = %s and memberId = %s", (ctx.message.guild.id, ctx.message.author.id))
            embed = nextcord.Embed(title="XP", color=0xff00bb)
            embed.add_field(name=f"{ctx.message.author.display_name}", value=f"`XP: {cursor.fetchone()[0]}`")
            embed.set_thumbnail(ctx.message.author.display_avatar.url +"?size=1024")
            await ctx.reply(embed=embed)
            return
        except:
            await ctx.reply("You don't have any XP")
            return


        
    @commands.command()
    async def xptop(self, ctx):
        if self.db == None:
            await ctx.reply("Squidward")
            return
        cursor:mysql.connector.connection.MySQLCursor = self.db.cursor()
        cursor.execute("SELECT memberXp, memberId FROM xp WHERE serverId = %s ORDER BY memberXp DESC", [str(ctx.message.guild.id)])
        embed = nextcord.Embed(title="XP Leaderboards", color=0xff00bb)
        data = cursor.fetchall()
        for i in range(min(len(data), 5)):
            embed.add_field(name=f"{i+1}.", value=f"<@{data[i][1]}>: `{data[i][0]}`", inline=False)
        
        await ctx.send(embed = embed)
        
    @commands.command()
    async def givexp(self, ctx, memb, xp):
        if memb.startswith("<@"):
            memb = memb[2:len(memb)-1]
        if self.db is None:
            print("No db?")
            return
        if ctx.message.author.guild_permissions.manage_guild == False:
            await ctx.reply("To be fair, even I don't know why you thought you can do this")
            return
        await self.storeXP([{"server":ctx.guild.id, "user":memb.id, "xp":xp}])
        
    @givexp.error
    async def info_error(ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect arguments.")
