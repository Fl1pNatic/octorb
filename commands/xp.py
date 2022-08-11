import nextcord
from nextcord.ext import commands
import asyncio

nextcord.Message.author.id

class xp(commands.Cog):
    bot: nextcord.Bot()
    def __init__(self, bot):
        self.bot = bot

    @bot.event()
    async def on_message(message: nextcord.Message, messageCounts = {nextcord.Message.guild.id:{nextcord.Message.author.id: nextcord.Message}}):
        if not message.guild.id in messageCounts:
            messageCounts[message.guild.id] = {}

        if not message.author.id in messageCounts:
            messageCounts[message.guild.id][message.author.id] = 1
            return
        messageCounts[message.guild.id][message.author.id] += 1

    async def calcXP(mess):
        while True:
            await asyncio.sleep(2)
            print(1)

    async def storexp(usrID,guildID,xp):
        pass