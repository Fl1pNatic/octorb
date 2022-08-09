# 🐙SQUID GAMES!11!1!1!11!1!1!1
import os
import nextcord
import random
from nextcord.ext import commands
import asyncio
from dotenv import dotenv_values, load_dotenv

from commands.fun import Fun
from commands.moderation import Moderation
from commands.other import Other

load_dotenv()

TOKEN = dotenv_values()["TOKEN"]

guildid = 1005860045919100958

#game = nextcord.Game(random.choice(game_list))
game = nextcord.Game("sq!help for commands list")

# intents.
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="sq!",
                   activity=game,
                   intents=intents,
                   help_command=None)

bot.add_cog(Fun(bot))
bot.add_cog(Other(bot))
bot.add_cog(Moderation(bot))


@bot.event
async def on_ready():
    print(f"It's {bot.user}in' time")

# Helper Commands
async def getuser(userid):
    guild = bot.get_guild(guildid)
    user = await guild.fetch_member(userid)
    return user

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(guildid)
    role = nextcord.utils.get(guild.roles, name='Member')
    user = await getuser(member.id)
    await user.add_roles(role)

bot.run(TOKEN)
