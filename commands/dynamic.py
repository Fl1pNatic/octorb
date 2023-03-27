import discord
from discord.ext import commands
import dotenv
import typing

imageLimit = 100

class dynamic(commands.Cog):
    def __init__(self, bot):
        gallery_id = 1031954555040170137
        if(bot.devmode):
            gallery_id = 1047158396966678560
        self.bot = bot
        self.galleryChannel = bot.get_channel(gallery_id)

    @commands.group()
    async def quickcommand(self, ctx):
        if ctx.invoked_subcommand is None:
                await ctx.reply("Use create, delete, or list!")
    # Quick commands
    @quickcommand.command(name="create", description="Creates a quick command.")
    @commands.has_guild_permissions(manage_messages=True)
    async def qcreate(self, ctx: commands.Context, command_name: str, *, message: str):
        """
        Parameters
        ------------
        command_name
            The name of the quick command to create
        message
            The content of the quick command
        """
        cursor = self.bot.db.cursor()
        command_name = command_name.replace("'", "\'").replace('"', '\"')
        message = message.replace("'", "\'").replace('"', '\"')
        cursor.execute("SELECT COUNT(*) FROM quickCommands WHERE serverId = ? AND command = ?;", (ctx.guild.id, command_name))
        currentAmount = cursor.fetchone()
        if currentAmount[0] != 0:
            cursor.execute("UPDATE quickCommands SET output = ? WHERE serverId = ? AND command = ?",
                           (message, ctx.guild.id, command_name))
        else:
            cursor.execute("INSERT INTO quickCommands VALUES ( ?, ?, ? )",
                           (ctx.guild.id, command_name, message))
        self.bot.db.commit()
        await ctx.send("Created quick command.")

    @quickcommand.command(name="delete", description="Deletes a quick command.")
    @commands.has_guild_permissions(manage_messages=True)
    async def qdelete(self, ctx: commands.Context, command_name: str):
        """
        Parameters
        ------------
        command_name
            The name of the command to delete
        """
        cursor = self.bot.db.cursor()
        command_name = command_name.replace("'", "\'").replace('"', '\"')
        cursor.execute("DELETE FROM quickCommands WHERE serverId = ? AND command = ?;", (ctx.guild.id, command_name))
        self.bot.db.commit()
        if cursor.rowcount == 0:
            await ctx.send("No quick command with this name.")
            return
        await ctx.send("Deleted quick command.")

    @quickcommand.command(name="list", description="Lists all the server's quickcommands.")
    async def qlist(self, ctx: commands.Context):
        cursor = self.bot.db.cursor()
        cursor.execute("SELECT command FROM quickCommands WHERE serverId = ?", (ctx.guild.id,))
        embed = discord.Embed(
            title="Quick commands list.",
            color=0xff00bb,
            description="Use like any other command! Use `quickcommand create` to create and `quickcommand delete` to delete."
        )
        commands = cursor.fetchall()
        cL = ""
        for command in commands:
            cL = cL + command[0] + ", "
        cL = cL[0:-2]
        embed.add_field(name="List", value=cL, inline=True)
        await ctx.send(embed=embed)

    # Gallery

    @commands.group(description="Shows the specific picture/video from the gallery, or allows for other gallery actions.")
    async def gallery(self, ctx: commands.Context, media_id: typing.Optional[int]):
        """
        Parameters
        ------------
        media_id
            The specific image/video you want to see
        """
        if ctx.invoked_subcommand is not None:
            return
        if media_id is None:
            await ctx.reply("Please use gallery [media id], gallery add [media], gallery count, or gallery delete [media id].")
            return
        cursor = self.bot.db.cursor()
        cursor.execute( 
            "SELECT picUrl FROM gallery WHERE id = ? AND serverId = ?", (media_id, ctx.guild.id))
        result = cursor.fetchall()
        if len(result) == 0:
            await ctx.send("No media found with that id.")
            return
        result = result[0]
        if result[0] == "0":
            await ctx.send("It appears this content has been deleted.")
            return
        await ctx.send(f"{result[0]}")

    @gallery.command(name="count", description="Gets the number of media in the server's gallery.")
    async def gcount(self, ctx: commands.Context):
        if self.bot.db is None:
            await ctx.send("There are 69 images.")
        cursor = self.bot.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM gallery WHERE serverId = ? AND NOT picUrl = '0'", (ctx.guild.id, ))
        count = cursor.fetchone()[0]
        await ctx.send(f"There are {count} things stored.")

    @gallery.command(name="add", description="Adds the media to the gallery.")
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def gadd(self, ctx: commands.Context, media: discord.Attachment):
        """
        Parameters
        ------------
        media
            The image/video you want to add
        """
        try:
            if not media.content_type.startswith("image/"):
                if not media.content_type.startswith("video/"):
                    await ctx.send("File does not appear to be an image/video.")
                    return
            galleryChannelMessage: discord.Message = await self.galleryChannel.send(file=await media.to_file())
            media = galleryChannelMessage.attachments[0]
            cursor = self.bot.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM gallery WHERE serverId = ?", (ctx.guild.id,))
            count = cursor.fetchone()[0]
            cursor.close()
            replaceDeleted = False
            if count >= imageLimit:
                cursor = self.bot.db.cursor()
                cursor.execute( 
                    "SELECT id FROM gallery WHERE serverId = ? AND picUrl = '0'", (ctx.guild.id,))
                set0 = cursor.fetchall()
                cursor.close()
                if len(set0) < 1:
                    await ctx.send("Max content amount reached for this guild.")
                    return
                replaceDeleted = set0[0][0]
            imageId = count
            if replaceDeleted is not False:
                imageId = replaceDeleted

            cursor = self.bot.db.cursor()
            if replaceDeleted is False:
                cursor.execute( "INSERT INTO gallery VALUES (?, ?, ?)",
                            (ctx.guild.id, count+1, media.url))
                await ctx.send(f"Added media with id {count + 1}")
                return
            cursor.execute( "UPDATE gallery SET picUrl = ? WHERE serverId = ? AND id = ?",
                        (media.url, ctx.guild.id, replaceDeleted))
            await ctx.send(f"Added media with id {replaceDeleted}")
        except Exception as e:
            print(e)

    @gallery.command(name="delete", description="Deletes media from the gallery.")
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def gdelete(self, ctx: commands.Context, media_id: int):
        """
        Parameters
        ------------
        media_id
            The image/video to delete
        """
        cursor = self.bot.db.cursor()
        cursor.execute( 
            "UPDATE gallery SET picUrl = '0' WHERE serverId = ? AND id = ?", (ctx.guild.id, media_id))
        await ctx.send("Deleted content from gallery.")
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Command, error: Exception):
        if not isinstance(error, commands.errors.CommandNotFound):
            #await self.bot.on_command_error(ctx, error)
            return
        if self.bot.db is None:
            return
        command = str(error)[9:-14]
        cursor = self.bot.db.cursor()
        command = command.replace("'", "\'").replace('"', '\"')
        cursor.execute( 
            "SELECT output FROM quickCommands WHERE serverId = ? AND command = ?", (ctx.guild.id, command))

        returns = cursor.fetchall()
        if len(returns) == 0:
            return

        await ctx.channel.send(returns[0][0])

async def setup(bot):
    await bot.add_cog(dynamic(bot))