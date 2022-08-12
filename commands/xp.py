from math import log
from concurrent.futures import process
import random
import nextcord
from nextcord.ext import commands
import asyncio
xp = {}

class xp(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.messageCounts = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.processXP()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        print(self.messageCounts)
        if message.author.bot or message.guild == None:
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
        for s in self.messageCounts.keys():
            for u in self.messageCounts[s].keys():
                uX = round(log(self.messageCounts[s][u])+5,0)
                await self.storeXP(s, u, uX)
        self.messageCounts = {}

    async def storeXP(self, serverID, userID, userXP):
        pass