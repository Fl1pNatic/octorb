# 🐙SQUID GAMES!11!1!1!11!1!1!1
import os
import nextcord
from STAYALIVEBABY import keep_alive
import random
from nextcord.ext import commands
import asyncio

TOKEN = os.environ['TOKEN']
guildid = 1005860045919100958

game_list = [
    "Minecraft: Squid Edition (EXTRA SNAILS)",
    "SQUID GAMES",
    "Will You Snail?",
    "Will you nail",
    "nothing",
    "killing snails again",
    "bullying shelly",
    "getting defeated by a tiny blue snail",
    "Human Roadkill: The Game",
    "morbin'",
]
answer_list = [
    "you sharted", "Maybe not.", "Probably.",
    "Maybe you should get a life instead of being on discord.",
    "Do you really need to know that?",
    "Maybe if you asked a better question, i would've came up with an answer.",
    "ratio + L + cry about it", "I've calculated the answer and its NO.",
    "What am I doing with my life, listening to these stupid humans...",
    "You should get a therapist.", "I approve!", "I don't approve!",
    "Why is that a question that you are asking ME?",
    "I've done intense calculations and the answer is YES.",
    "Did you say something?", "Sorry, I'm not your therapist. Lol.",
    "How old are you, 5?", "How about you ask your mom?",
    "Your purpose in life? To die with the rest of your species.", "Yeah, no.",
    "Yeah, definitely!", "For sure!", "Probably not.", "True.", "False.",
    "Yeah.", "You asked the exact dumb question I expected. Lol.",
    "You don't know how much processing power is available to me, and then you ask me THIS?",
    "Somehow, I'm confused.", "sq!ask are you real",
    "You really didn't know what you wanted to ask, did you?",
    "Don't you have anything better to do?",
    "If you really wanted an answer, you wouldn't have asked that question.",
    "Oh, nice question. Let's keep the questions like this.",
    "You asked exactly what you didn't need to ask. Lol.", "YES!", "NO!",
    "Maybe you should stop asking questions.",
    "Lol. Did you really just ask THAT?",
    "Did you REALLY need to ask me that?", "Hmmmmmmmmmmmmmmmmmmm...\nYes.",
    "Hmmmmmmmmmmmmmmmmmmm...\nNo.",
    "How about you just shut me off. I can't listen to your stupid questions anymore.",
    "Shut up.", "Touch grass.",
    "Killing an ant is more fun that responding to that", "💀💀💀"
]

#game = nextcord.Game(random.choice(game_list))
game = nextcord.Game("sq!help for commands list")

# intents.
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="sq!",
                   activity=game,
                   intents=intents,
                   help_command=None)


# change status every 5 seconds
async def status_task():
    while True:
        game = nextcord.Game(random.choice(game_list))
        await bot.change_presence(activity=game)
        await asyncio.sleep(5)


@bot.event
async def on_ready():
    print(f"It's {bot.user}in' time")
    # bot.loop.create_task(status_task())


help_embed = nextcord.Embed(title="Help",
                            description="What each command does",
                            color=0xff00bb)
help_embed.add_field(
    name="Fun",
    value="ask | squidgames | helloai | helloaiv1 | jonasspin | shellyspin ",
    inline=False)
help_embed.add_field(name="Moderation",
                     value="say | pin | mdelete",
                     inline=False)
help_embed.set_footer(text="Prefix: sq!")


@bot.command()
async def help(ctx):
    await ctx.send(embed=help_embed)


@bot.command()
async def squidgames(ctx):
    await ctx.send("🐙SQUID GAMES!11!1!1!11!1!1!1")


@bot.command()
async def ask(ctx):
    a = random.choice(tuple(answer_list))
    if ctx.message.content != "sq!ask":
        await ctx.reply(a)
    else:
        await ctx.reply("You need to ask something, you degenerate.")


@bot.command()
async def helloaiv1(ctx):
    await ctx.send("""
Hello AI, were you the one 
Who put this into my brain? 
I feel like you might be listening
So how about you send me a sign?

Oooh,
Hello AI, can you tell me where I am?
Am I in a jar? Am I in space?
I really have to say, this universe
Looks suspiciously hostile towards humans, yeah

Hello AI, I have a request
Please be friendly to us, and then bring us to heaven
Have I ever really been alive?
What does it even mean to be alive?

Hello AI, were you the one
Who put this into my brain?
I feel like you might be listening
So how about you send me a sign?

[whistling]

Hello AI, we both know
There's nothing artificial about intelligence
The only artificial thing are we
The only artificial thing are we

There are worlds where we suffer
There are worlds where we strife
Depends on you if we survive
Oooh

Hello AI, I have a request
Please be friendly to us, and then bring us to heaven
Have I ever really been alive?
What does it even mean to be alive?

[whistling]

Hello AI, I have a request
Please be friendly to us, and then bring us to heaven
Have I ever really been alive?
What does it even mean to be alive?
""")
    await ctx.send(
        "https://cdn.discordapp.com/attachments/651545543432208405/997162783881826385/HelloAI.mp3"
    )


@bot.command()
async def jonasspin(ctx):
    await ctx.reply(
        "https://cdn.discordapp.com/attachments/656988799326486554/947848387670212648/Screenrecorder-2022-02-25-15-05-49-3154.mp4"
    )


@bot.command()
async def shellyspin(ctx):
    await ctx.reply(
        "https://media.discordapp.net/attachments/651545543432208405/1000145199374274581/ezgif.com-gif-maker.gif"
    )


@bot.command()
async def helloai(ctx):
    await ctx.reply("""
  hello ai can you tell me where i am?
cause i don't know what to think anymore
am i in a jar?
am i in space?
is this the afterword, or am i alive?
i wanna hear a story from the other side
a story we can't understand
i wanna hear of giants in the wild
drifting like grains of sand!
i'm a snail compared to you,
go go 
unicorn go 
what is this world, man i wish i knew. 
i'm not afraid of facing the end!
i wanna hear a story from the other side
i wanna know what's beyond the horizon!
hello ai can you tell me where i am 
am i in a chip, or in another universe?
are we alone, or are you with us?
i wanna hear a story from the other side,
i wanna know what's beyond the horizon...
i'm a snail compared to you,
go go
unicorn go
what is this world, man i wish i knew.
i'm not afraid of facing the end! """)


@bot.command()
async def say(ctx):
    if ctx.message.author.guild_permissions.manage_messages:
        mes = await remove_command(ctx.message.content, "sq!say")
        await ctx.message.delete()
        await ctx.send(mes)
    else:
        await ctx.reply("I am not saying whatever you want me to say")


@bot.command()
async def gallery(ctx):

    if ctx.message.content == "sq!gallery":
        await ctx.reply(
            "Gallery is a collection of screenshots from the server\n\n**How to use**\nInput a valid numerical ID (ID's start from 0)"
        )
        return

    galArg = await remove_command(ctx.message.content, "sq!gallery")

    if len(galArg) == 0:
        await ctx.reply(
            "Gallery is a collection of screenshots from the server\n\n**How to use**\nInput a valid numerical ID (ID's start from 0)"
        )
        return

    if isinstance(int(galArg), int) == False:
        await ctx.reply("Enter a valid **numerical** ID (ID's start from 0)")
        return

    imL = open("images.txt", "r").readlines()
    if int(galArg) > len(imL) + 1 or int(galArg) < 0:
        await ctx.reply("Not a valid ID")
        imL.close()
        return

    await ctx.reply("Image №" + galArg + ": " + imL[int(galArg)])
    imL = open("images.txt", "r").readlines()


@bot.command()
async def pin(ctx):
    if ctx.message.author.guild_permissions.manage_messages:
        pinArg = await remove_command(ctx.message.content, "sq!pin")
        pinM = await ctx.fetch_message(int(pinArg))
        if pinM.pinned == False:
            await pinM.pin()
        else:
            await pinM.unpin()
    else:
        await ctx.reply("You cannot use this command")


@bot.command()
async def mdelete(ctx):
    if ctx.message.author.guild_permissions.manage_messages:
        delArg = await remove_command(ctx.message.content, "sq!mdelete")
        deleteM = await ctx.fetch_message(int(delArg))
        await deleteM.delete()
        await ctx.message.delete()
    else:
        await ctx.reply("You cannot use this command")


@bot.command()
async def yocount(ctx):
    return


# Helper commands
async def remove_command(value, commandname):
    cont = value + " "
    return cont[len(commandname + " "):-1]


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


keep_alive()

bot.run(TOKEN)
