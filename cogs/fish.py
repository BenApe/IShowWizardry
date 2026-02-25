import discord
import random
import userlevel

from discord.ext import commands
from discord import app_commands

class fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="fishing_rod", description="Fish", aliases=["fish", "fishingrod"])
    async def fishing_rod(self, ctx:commands.Context):
        user = ctx.author
        
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        
        user_data = userlevel.userlevel(user.id, ctx.guild.id)
        
        DEFAULT_WEIGHT = 10
        
        fishes = {
            "Bass":
                {"sell": 2, "weight": DEFAULT_WEIGHT},
            "Cod":
                {"sell": 2, "weight": DEFAULT_WEIGHT},
            "Salmon":
                {"sell": 2, "weight": DEFAULT_WEIGHT},
            "Tuna":
                {"sell": 4, "weight": DEFAULT_WEIGHT},
            "Carp":
                {"sell": 3, "weight": DEFAULT_WEIGHT},
            "Tilapia":
                {"sell": 3, "weight": DEFAULT_WEIGHT},
            "Herring":
                {"sell": 2, "weight": DEFAULT_WEIGHT},
            "Rainbow Trout":
                {"sell": 6, "weight": DEFAULT_WEIGHT},
            "Catfish":
                {"sell": 3, "weight": DEFAULT_WEIGHT},
            "Halibut":
                {"sell": 3, "weight": DEFAULT_WEIGHT},
            "Swordfish":
                {"sell": 4, "weight": DEFAULT_WEIGHT},
            "Pike":
                {"sell": 2, "weight": DEFAULT_WEIGHT},
            "Mackerel":
                {"sell": 2, "weight": DEFAULT_WEIGHT},
            "Sardine":
                {"sell": 1, "weight": DEFAULT_WEIGHT},
            "Red Herring":
                {"sell": -2, "weight": 3},
            "Whale":
                {"sell": 20, "weight": 1},
            "Nothing":
                {"sell": 0, "weight": DEFAULT_WEIGHT*4}
        }
        
        rarities = {
            "Abysmal": 
                {"sell": 0, "weight": 5},
            "Bad":
                {"sell": 1, "weight": 25},
            "Mediocre":
                {"sell": 3, "weight": 40},
            "Good":
                {"sell": 6, "weight": 25},
            "Amazing":
                {"sell": 10, "weight": 4},
            "Legendary":
                {"sell": 20, "weight": 1}
        }
        
        sizes = {
            "Miniscule":
                {"sell": -2, "weight": 5},
            "Tiny":
                {"sell": 0, "weight": 10},
            "Small":
                {"sell": 1, "weight": 20},
            "Medium":
                {"sell": 2, "weight": 35},
            "Big":
                {"sell": 3, "weight": 15},
            "Huge":
                {"sell": 4, "weight": 10},
            "Gigantic":
                {"sell": 5, "weight": 4},
            "Leviathan":
                {"sell": 10, "weight": 1}
        }
        
        fish_list = list(fishes.keys())
        rarity_list = list(rarities.keys())
        size_list = list(sizes.keys())
        
        fish_weights = [item["weight"] for item in fishes.values()]
        rarity_weights = [item["weight"] for item in rarities.values()]
        size_weights = [item["weight"] for item in sizes.values()]
        
        fishyfishy = random.choices(fish_list, weights=fish_weights, k=1)[0]
        rarity = random.choices(rarity_list, weights=rarity_weights, k=1)[0]
        size = random.choices(size_list, weights=size_weights, k=1)[0]
        
        value = fishes.get(fishyfishy).get("sell") + rarities.get(rarity).get("sell") + sizes.get(size).get("sell")
        
        xp_gain = int(value/5)
        user_data.add_xp(xp_gain)
        
        fish = {
            fishyfishy:{
                "rarity": rarity,
                "size": size,
                "value": value
            }
        }
        
        catch = f"You caught a {size.lower()}-sized {rarity.lower()} {fishyfishy.lower()} worth {value} mana!\n-# +{xp_gain} XP"
        
        if fishyfishy == "Nothing":
            catch = "You caught nothing!"
        
        await ctx.reply(catch)

async def setup(bot):
    await bot.add_cog(fish(bot))