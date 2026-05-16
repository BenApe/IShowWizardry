import discord

from discord import app_commands
from discord.ext import commands
from userstats import userstats

class stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="stats", description="Get stats for yourself or another user.")
    async def get_stats(self, ctx:commands.Context, user:discord.User = None):
        user = user if user else ctx.author
        statsuser = userstats(user.id)
        
        embed = discord.Embed(
            description=statsuser.to_string()
        )
        embed.set_author(
            name=f"{user.display_name}'s Stats",
            icon_url=user.display_avatar.url
        )
        
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(stats(bot))