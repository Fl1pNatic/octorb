from discord.ext import commands
from random import choice

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

yo_vars = ["yo", "yoyo", "yoyoyo", "toe"]

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ask(self, ctx, *question: any):
        a = choice(tuple(answer_list))
        await ctx.reply(a)

    @commands.command()
    async def gallery(self, ctx, imageId: int):
        galArg = imageId

        if isinstance(int(galArg), int) == False:
            await ctx.reply("Enter a valid **numerical** ID (ID's start from 0)")
            return
        
        imL = open("images.txt", "r").readlines()
        
        if int(galArg) > len(imL) - 1 or int(galArg) < 0:
            await ctx.reply("Not a valid ID")
            return

        await ctx.reply("Image №" + galArg + ": " + imL[int(galArg)])

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def createquickcommand(self, ctx, commandName: str, *, message: str):
        cursor = self.bot.db.cursor()
        cursor.execute(f"SELECT * FROM quickCommands WHERE serverId = '{ctx.guild.id}' AND command = '{commandName}';")
        command = f"INSERT INTO quickCommands VALUES ( '{ctx.guild.id}', '{commandName}', '{message}' )"
        if cursor.rowcount != 0:
            command = f"UPDATE quickCommands SET output = '{message}' WHERE serverId = '{ctx.guild.id}' AND command = '{commandName}'"
        cursor.execute(command)
        self.db.commit()
