from cmath import log
from concurrent.futures import process
import random
import nextcord
from nextcord.ext import commands
import asyncio
messageCounts = {}
xp = {}

class xp(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        print(messageCounts)
        if message.author.bot:
            return
        if not message.guild.id in messageCounts:
            messageCounts[message.guild.id] = {}

        if not message.author.id in messageCounts[message.guild.id]:
            messageCounts[message.guild.id][message.author.id] = 1
            return
        messageCounts[message.guild.id][message.author.id] += 1
        print(messageCounts[message.guild.id][message.author.id])


        async def processXP():
            while True:
                await asyncio.sleep(60)
                await calcXP()
                messageCounts = {}

        async def calcXP():
            for s in messageCounts.keys():
                for u in messageCounts[s].keys():
                    uX = log(messageCounts[s][u])
                    await storeXP(s, u, uX)

        async def storeXP(serverID, userID, userXP):
            pass