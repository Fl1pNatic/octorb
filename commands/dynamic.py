import discord
from discord.ext import commands
from discord import app_commands
import dotenv

imageLimit = 100

class dynamic(commands.Cog):
    def __init__(self, bot):
        gallery_id = 1031954555040170137
        if(bot.devmode):
            gallery_id = 1047158396966678560
        self.bot = bot
        self.galleryChannel = bot.get_channel(gallery_id)


    quickcommand = app_commands.Group(name='quickcommand', description='Commands for quick commands.')
    # Quick commands
    @quickcommand.command(name="create", description="Creates a quick command.")
    @commands.has_guild_permissions(manage_messages=True)
    async def qcreate(self, ctx: discord.Interaction, command_name: str, *, message: str):
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
        self.bot.dbexec(cursor, 
            "SELECT COUNT(*) FROM quickCommands WHERE serverId = %s AND command = %s;", (ctx.guild.id, command_name))
        currentAmount = cursor.fetchone()
        if currentAmount[0] != 0:
            self.bot.dbexec(cursor, "UPDATE quickCommands SET output = %s WHERE serverId = %s AND command = %s",
                           (message, ctx.guild.id, command_name))
        else:
            self.bot.dbexec(cursor, "INSERT INTO quickCommands VALUES ( %s, %s, %s )",
                           (ctx.guild.id, command_name, message))
        self.bot.db.commit()
        await ctx.response.send_message("Created quick command.")

    @quickcommand.command(name="delete", description="Deletes a quick command.")
    @commands.has_guild_permissions(manage_messages=True)
    async def qdelete(self, ctx: discord.Interaction, command_name: str):
        """
        Parameters
        ------------
        command_name
            The name of the command to delete
        """
        cursor = self.bot.db.cursor()
        command_name = command_name.replace("'", "\'").replace('"', '\"')
        self.bot.dbexec(cursor, 
            "DELETE FROM quickCommands WHERE serverId = %s AND command = %s;", (ctx.guild.id, command_name))
        self.bot.db.commit()
        if cursor.rowcount == 0:
            await ctx.response.send_message("No quick command with this name.")
            return
        await ctx.response.send_message("Deleted quick command.")

    @quickcommand.command(name="list", description="Lists all the server's quickcommands.")
    async def qlist(self, ctx: discord.Interaction):
        cursor = self.bot.db.cursor()
        self.bot.dbexec(cursor, 
            "SELECT command FROM quickCommands WHERE serverId = %s", (ctx.guild.id,))
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
        await ctx.response.send_message(embed=embed)

    # Gallery

    gallery = app_commands.Group(name="gallery", description="Gallery commands.")

    @gallery.command(name="count", description="Gets the number of media in the server's gallery.")
    async def gcount(self, ctx: discord.Interaction):
        if self.bot.db is None:
            await ctx.response.send_message("There are 69 images.")
        cursor = self.bot.db.cursor()
        self.bot.dbexec(cursor, 
            "SELECT COUNT(*) FROM gallery WHERE serverId = %s AND NOT picUrl = '0'", ctx.guild.id)
        count = cursor.fetchone()[0]
        await ctx.response.send_message(f"There are {count} things stored.")

    @gallery.command(name="add", description="Adds the media to the gallery.")
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def gadd(self, ctx: discord.Interaction, media: discord.Attachment):
        """
        Parameters
        ------------
        media
            The image/video you want to add
        """
        try:
            if not media.content_type.startswith("image/"):
                if not media.content_type.startswith("video/"):
                    await ctx.response.send_message("File does not appear to be an image/video.")
                    return
            galleryChannelMessage: discord.Message = await self.galleryChannel.send(file=await media.to_file())
            media = galleryChannelMessage.attachments[0]
            cursor = self.bot.db.cursor()
            self.bot.dbexec(cursor, 
                "SELECT COUNT(*) FROM gallery WHERE serverId = %s", (ctx.guild.id,))
            count = cursor.fetchone()[0]
            cursor.close()
            replaceDeleted = False
            if count >= imageLimit:
                cursor = self.bot.db.cursor()
                self.bot.dbexec(cursor, 
                    "SELECT id FROM gallery WHERE serverId = %s AND picUrl = '0'", (ctx.guild.id,))
                set0 = cursor.fetchall()
                cursor.close()
                if len(set0) < 1:
                    await ctx.response.send_message("Max content amount reached for this guild.")
                    return
                replaceDeleted = set0[0][0]
            imageId = count
            if replaceDeleted is not False:
                imageId = replaceDeleted

            cursor = self.bot.db.cursor()
            if replaceDeleted is False:
                self.bot.dbexec(cursor, "INSERT INTO gallery VALUES (%s, %s, %s)",
                            (ctx.guild.id, count+1, media.url))
                await ctx.response.send_message(f"Added media with id {count + 1}")
                return
            self.bot.dbexec(cursor, "UPDATE gallery SET picUrl = %s WHERE serverId = %s AND id = %s",
                        (media.url, ctx.guild.id, replaceDeleted))
            await ctx.response.send_message(f"Added media with id {replaceDeleted}")
        except Exception as e:
            print(e)

    @gallery.command(name="delete", description="Deletes media from the gallery.")
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def gdelete(self, ctx: discord.Interaction, media_id: int):
        """
        Parameters
        ------------
        media_id
            The image/video to delete
        """
        cursor = self.bot.db.cursor()
        self.bot.dbexec(cursor, 
            "UPDATE gallery SET picUrl = '0' WHERE serverId = %s AND id = %s", (ctx.guild.id, media_id))
        await ctx.response.send_message("Deleted content from gallery.")

    @gallery.command(name="show", description="Shows the specific picture/video from the gallery.")
    async def gshow(self, ctx: discord.Interaction, media_id: int):
        """
        Parameters
        ------------
        media_id
            The specific image/video you want to see
        """
        cursor = self.bot.db.cursor()
        self.bot.dbexec(cursor, 
            "SELECT picUrl FROM gallery WHERE id = %s AND serverId = %s", (media_id, ctx.guild.id))
        result = cursor.fetchall()
        if len(result) == 0:
            await ctx.response.send_message("No media found with that id.")
            return
        result = result[0]
        if result[0] == "0":
            await ctx.response.send_message("It appears this content has been deleted.")
            return
        await ctx.response.send_message(f"{result[0]}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Command, error: Exception):
        if self.bot.db is None:
            return
        if not isinstance(error, commands.errors.CommandNotFound):
            raise (error)
        command = str(error)[9:-14]
        cursor = self.bot.db.cursor()
        command = command.replace("'", "\'").replace('"', '\"')
        self.bot.dbexec(cursor, 
            "SELECT output FROM quickCommands WHERE serverId = %s AND command = %s", (ctx.guild.id, command))

        returns = cursor.fetchall()
        if len(returns) == 0:
            return

        await ctx.channel.send(returns[0][0])
