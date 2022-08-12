from math import log
from concurrent.futures import process
import random
import nextcord
from nextcord.ext import commands
import asyncio
import mysql.connector
xp = {}

class xp(commands.Cog):
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.messageCounts = {}
        self.db:mysql.connector.MySQLConnection = db

    @commands.Cog.listener()
    async def on_ready(self):
        await self.processXP()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # print(self.messageCounts)
        if message.author.bot or message.guild is None:
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
            await asyncio.sleep(15)

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
    async def xp(self, ctx):
        if self.db == None:
            await ctx.reply("You have 69 XP")
            return
        cursor:mysql.connector.connection.MySQLCursor = self.db.cursor()
        cursor.execute("SELECT memberXp FROM xp WHERE serverId = %s and memberId = %s", (ctx.message.guild.id, ctx.message.author.id))
        await ctx.reply("You have ", cursor.fetchone([0]) + " XP")
