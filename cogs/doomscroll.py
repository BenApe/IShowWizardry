import discord
import random
import profanity_filter

from discord.ext import commands
from discord import app_commands

class doomscroll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="write_doomscroll", description="Write a doomscroll")
    async def doomscroll(self, ctx:commands.Context, evil_message:str):
        