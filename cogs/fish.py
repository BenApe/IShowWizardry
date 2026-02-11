import discord
import random

from discord.ext import commands
from discord import app_commands

class fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="fishing_rod", description="Fish")
    async def fishing_rod(self, ctx:commands.Context):
        fishes = [
            "bass",
            "cod",
            "salmon",
            "tuna",
            "sardine",
            "carp",
            "tilapia",
            "herring",
            "rainbow trout",
            "catfish",
            "halibut",
            "swordfish",
            "pike",
            "mackerel"
        ]
        
        catch = f"You caught a {random.choice(fishes)}!"
        
        await ctx.reply(catch)

async def setup(bot):
    await bot.add_cog(fish(bot))