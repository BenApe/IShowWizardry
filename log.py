import discord

from discord.ext import commands
from discord.ui import Button, View
from botutils import savejson, loadjson, get_discord_timestamp
from banned_users import BannedUsers

LOG_CHANNEL_ID = 1478912785000824882

async def log_message(user:discord.User, message:str, iso_time:str, bot:commands.Bot, command_used:str, server:discord.Guild):
    channel = await bot.fetch_channel(LOG_CHANNEL_ID)
    timestamp = get_discord_timestamp(iso_time=iso_time, style="f")
    
    embed = discord.Embed(
        description=f"'{message}'\n-# Sent on {timestamp}"
    )
    
    embed.set_author(name=f"UID: {user.id}", icon_url=user.avatar.url)
    embed.set_footer(text=f"Executed `{command_used}` for {user.global_name} in {server.name}.")
    
    view = LogView(user=user)
    await channel.send(embed=embed, view=view)

class LogView(View):
    def __init__(self, user:discord.User):
        super().__init__()
        self.user = user
        self.bannedusers = BannedUsers()
    
    @discord.ui.button(label="Ban user", style=discord.ButtonStyle.red)
    async def ban_btn(self, interaction:discord.Interaction, button:Button):
        self.bannedusers.update_user(user_id=self.user.id)
        
        await interaction.response.send_message(f"User {self.user.global_name} is now banned from using /say until {self.bannedusers.get_timestamp(self.user.id)}.")