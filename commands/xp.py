from email import message
import nextcord
from nextcord.ext import commands

class xp(commands.Cog):
    bot = commands.Bot(intents=nextcord.Intents.all())
    def __init__(self, bot) -> None:
        self.bot = bot

    @bot.event
    async def on_message(message: nextcord.Message):
        messageCounts = {message.guild.id:{message.author.id: message}}
        if message.author.bot:
            print("vej")
            return
        if not message.guild.id in messageCounts:
            messageCounts[message.guild.id] = {}
            print("vrej")

        if not message.author.id in messageCounts:
            messageCounts[message.guild.id][message.author.id] = 1
            print("vrebj")
            return
        messageCounts[message.guild.id][message.author.id] += 1
        print(messageCounts[message.guild.id][message.author.id])
        # await calcXP(messageCounts)
        await message.channel.send(messageCounts[message.guild.id][message.author.id])

    async def calcXP():
        pass