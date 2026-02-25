import discord
import math
import userlevel

from userlevel import lvl_to_xp, xp_to_lvl
from discord.ext import commands
from discord import app_commands
from botutils import loadjson, savejson

# Mana is won from wizard duels and earned by selling fish
# 1 mana gained = 1 xp
# xp goes towards leveling up

class levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # MOD COMMANDS
    @commands.hybrid_command(name="edit_level", description="(MOD) Edit a user's level or xp")
    @commands.has_permissions(kick_members=True)
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Set level", value="level"),
            app_commands.Choice(name="Add/subtract xp", value="xp")
        ]
    )
    async def edit_level(self, ctx:commands.Context, user:discord.User, action:str, amount:int):
        server_id = ctx.guild.id
        user_data = userlevel.userlevel(user.id, server_id)
        
        if action == "level":
            amount = 0 if amount < 0 else amount
            level = amount
            xp = lvl_to_xp(level)
            await ctx.send(f"Edited {user.mention}'s {action}.\n> **Previous:**\n> Level: {user_data.get_level()} | XP: {user_data.get_xp()}\n\n> **Now:**\n> Level: {level} | XP: {xp}\n-# (Set level to {level})")
            user_data.set_user_data({user.id: {"xp": xp, "level": level}})
        
        elif action == "xp":
            xp = user_data.get_xp() + amount
            level = xp_to_lvl(xp)
            await ctx.send(f"Edited {user.mention}'s {action}.\n> **Previous:**\n> Level: {user_data.get_level()} | XP: {user_data.get_xp()}\n\n> **Now:**\n> Level: {level} | XP: {xp}\n-# (Changed xp total by {amount})")
            user_data.set_user_data({user.id: {"xp": xp, "level": level}})
        
    @commands.hybrid_command(name="level", description="Get your wizard level")
    async def level(self, ctx:commands.Context, user:discord.User = None):
        server_id = ctx.guild.id
        
        if user == None:
            user = ctx.author
            
            if isinstance(ctx, discord.Interaction):
                user = ctx.user
        
        user_data = userlevel.userlevel(user_id=user.id, server_id=server_id)
        user_level = user_data.get_level()
        user_xp = user_data.get_xp()
        
        progress_bar = user_data.progressbar()
        
        embed = discord.Embed(
            title=f"{user.display_name} is a Level {user_level} Wizard!",
            description=progress_bar
            )
        
        embed.set_footer(text=f"({user_xp} XP/{user_data.xp_required()} XP)")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(levels(bot))