import discord
import random
import userlevel

from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta, timezone
from botutils import savejson, loadjson, get_discord_timestamp

POOL_CAP = 15

class fishpool():
    def __init__(self, user_id:int, count:int = POOL_CAP, last_updated=None):
        self.user_id = user_id
        self.count = count
        self.last_updated = last_updated or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            self.user_id:{
                "count": self.count,
                "last_updated": self.last_updated
            }
        }
    
    @classmethod
    def from_dict(cls, data:dict):
        return cls(
            user_id = list(data.keys())[0],
            count = data.get("count"),
            last_updated = data.get("last_updated")
        )

class poolmanager():
    def __init__(self):
        self.pool_path = "user_data/fish/user_pools"
        self.user_pools = loadjson(self.pool_path)
    
    def save_pools(self):
        savejson(self.pool_path, self.user_pools)
    
    def get_pool(self, user_id):
        if user_id not in self.user_pools:
            self.user_pools.update(fishpool(user_id).to_dict())
            self.save_pools()
        
        return self.user_pools.get(user_id)
    
    def update_pool(self, user_id):
        pool = self.get_pool(user_id)
        last = datetime.fromisoformat(pool.get("last_updated"))
        now = datetime.now()
        minutes_passed = int((now - last).total_seconds() / 60)
        
        if pool.get("count") < 15:
            if minutes_passed > 0:
                pool["count"] = min(pool.get("count") + minutes_passed, 15)
                pool["last_updated"] = now.isoformat()
                self.save_pools()
            
            return pool.get("count")
        
        else:
            self.user_pools.pop(user_id)
            self.save_pools()
            return 15

    def decrement_pool(self, user_id, amount:int=1):
        pool = self.get_pool(user_id)
        pool["count"] = max(pool.get("count") - amount, 0)
        self.save_pools()
        
        return pool.get("count")
    
    def increment_pool(self, user_id, amount:int=1):
        pool = self.get_pool(user_id)
        pool["count"] = min(pool.get("count") + 1, 15)
        self.save_pools()
    
    def get_remaining_seconds(self, user_id):
        if user_id not in self.user_pools:
            return None
        
        start = self.user_pools.get(user_id).get("last_updated")
        timestamp = get_discord_timestamp(start, increment_minutes=1)
        return timestamp

pool_mngr = poolmanager()

class fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool_check.start()
    
    def cog_unload(self):
        self.pool_check.cancel()
        
    @tasks.loop(minutes=1)
    async def pool_check(self):
        # print(f"Updating pools for {len(pool_mngr.user_pools)} users...")
        
        for user_id in list(pool_mngr.user_pools.keys()):
            pool_mngr.update_pool(user_id)
    
    @pool_check.before_loop
    async def before_pool_check(self):
        await self.bot.wait_until_ready()
    
    @commands.hybrid_command(name="fish_pool", description="See how many fish are left in your pool.", aliases=["pool", "pond"])
    async def fish_pool(self, ctx:commands.Context):
        user = ctx.author
        
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        
        count = pool_mngr.update_pool(user.id)
        timestamp = pool_mngr.get_remaining_seconds(user.id)
        description = f"You have {count} fish left in your pond.\n-# Next fish {timestamp}" if count < 15 else f"You have {count} fish left in your pond.\n-# Your pond is full!"
        
        embed = discord.Embed(
            description=description,
            color=0x40c969
        )
        
        embed.set_author(name=f"{user.display_name}'s Pond", icon_url=user.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="fishing_rod", description="Fish", aliases=["fish", "fishingrod"])
    async def fishing_rod(self, ctx:commands.Context):
        user = ctx.author
        
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        
        user_data = userlevel.userlevel(user.id, ctx.guild.id)
        fish_ct = pool_mngr.decrement_pool(user_id=user.id)
        
        if fish_ct == 0:
            responses = [
                "You caught nothing!\n-# You can fish again ",
                "Seems like the pond is empty...\n-# You can fish again ",
                "No more fish! Try again ",
                "You ran out of bait!\n-# You can fish again ",
                "Pond is empty buddy.\n-# You can fish again ",
                "Overfishing is harmful to ecosystems!\n -# You can fish again ",
                "The line snapped!\n-# You can fish again ",
                "You lost the hook!\n-# You can fish again ",
                "The fish escaped...\n-# You can fish again "
            ]
            
            timestamp = pool_mngr.get_remaining_seconds(user.id)
            
            return await ctx.reply(content=f"{random.choice(responses)}{timestamp}", ephemeral=True)
        
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
                {"sell": 0, "weight": DEFAULT_WEIGHT*6}
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
            catch = "You lost a some of bait!"
            
            if random.randint(1, 100) < 66:
                catch = "You caught nothing!"
                pool_mngr.increment_pool(user_id=user.id)
        
        await ctx.reply(catch)


async def setup(bot):
    await bot.add_cog(fish(bot))