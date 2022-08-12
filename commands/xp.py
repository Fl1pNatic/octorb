from email import message
import nextcord
from nextcord.ext import commands
messageCounts = {}

class xp(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        print(messageCounts)
        if message.author.bot:
            print("vej")
            return
        if not message.guild.id in messageCounts:
            messageCounts[message.guild.id] = {}
            print("vrej")

        if not message.author.id in messageCounts[message.guild.id]:
            messageCounts[message.guild.id][message.author.id] = 1
            print("vrebj")
            return
        messageCounts[message.guild.id][message.author.id] += 1
        print(messageCounts[message.guild.id][message.author.id])
        # await calcXP(messageCounts)
        #await message.channel.send(messageCounts[message.guild.id][message.author.id])

    async def calcXP():
        pass