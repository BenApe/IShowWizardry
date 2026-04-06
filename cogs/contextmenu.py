import discord
import banned_words
import banned_users

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from log import log_message
from discord.ui import Modal, TextInput, Checkbox, Label

class contextmenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.say_ctx_menu = app_commands.ContextMenu(name="Say", callback=self.say_menu_callback)
        self.bot.tree.add_command(self.say_ctx_menu)
    
    async def cog_unload(self):
        self.bot.tree.remove_command(self.say_ctx_menu.name, type=self.say_ctx_menu.type)
    
    async def say_menu_callback(self, interaction:discord.Interaction, message:discord.Message):
        await interaction.response.send_modal(say_modal(message, self.bot))
        
class say_modal(Modal, title="Reply to a message"):
    def __init__(self, message:discord.Message, bot:commands.Bot):
        super().__init__()
        self.message = message
        self.bot = bot
        
        self.reply = TextInput(
            label="What do you want to say?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.reply)
        
        self.reply_ping = Label(text="Reply ping", component=Checkbox(default=True))
        self.add_item(self.reply_ping)
    
    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        
        bannedusers = banned_users.BannedUsers()
        timestamp = bannedusers.get_timestamp(user.id)
        
        if bannedusers.check_user(user.id) and timestamp != None:
            return await interaction.response.send_message(f"You've been banned from using this command until {timestamp}", ephemeral=True)
        
        banned = banned_words.BannedWords()
        banned.disable_tier(2)
        banned.disable_tier(3)
        banned.disable_tier(4)
        
        reply = f"{self.reply}"
        reply_words = reply.split(" ")
        
        await log_message(user=user, message=reply, iso_time=datetime.now().isoformat(), bot=self.bot, command_used="Say menu cmd", server=interaction.guild)
        
        for word in reply_words:
            if banned.isprofane(word):
                return await user.send(f"The word '{word}' is not permitted.")
        
        await self.message.reply(reply, mention_author=self.reply_ping.component.value)
        await interaction.response.send_message("Reply sent!", ephemeral=True, delete_after=1)

async def setup(bot):
    await bot.add_cog(contextmenu(bot))