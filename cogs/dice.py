import discord
import random

from discord.ext import commands
from discord import app_commands

class dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="die", description="Roll a die")
    async def die(self, ctx:commands.Context, sides:int = 6):
        result = random.randint(1, sides)
        
        await ctx.send(content=f"You rolled a {result}!")

async def setup(bot):
    await bot.add_cog(dice(bot))