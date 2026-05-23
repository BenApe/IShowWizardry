import discord

from discord import app_commands
from discord.ext import commands
from userstats import userstats, get_value_choices, collect_vals
from botutils import process_timer, ordinal
from datetime import datetime

VALUE_CHOICES = get_value_choices()

class stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_command(name="stats", description="Get stats for yourself or another user.")
    async def get_stats(self, ctx:commands.Context, user:discord.User = None):
        user = user if user else ctx.author
        statsuser = userstats(user.id)
        
        embed = discord.Embed(
            description=statsuser.to_string(),
            color=0x2ECC71
        )
        embed.set_author(
            name=f"{user.display_name}'s Stats",
            icon_url=user.display_avatar.url
        )
        
        await ctx.reply(embed=embed)
    
    @commands.hybrid_command(name="leaderboard", description="Get the leaderboard for a specific stat.")
    @app_commands.choices(
        type=VALUE_CHOICES,
        scope=[
            app_commands.Choice(name="Get the leaderboard for this server", value="server"),
            app_commands.Choice(name="Get the global leaderboard", value="global")
        ]
    )
    async def leaderboard(self, ctx:commands.Context, type:str, scope:str = "server"):
        timer = process_timer()
        all_values = collect_vals(type)
        member_vals = []
        name = type.replace("_", " ").title()
        title = f"Top Users for {name} "
        icon = self.bot.user.display_avatar.url
        top20 = ""
        author = ctx.author
        author_data = None
        
        if scope == "server":
            server = ctx.guild
            title += f"in {server.name}"
            if server.icon: icon = server.icon.url
            for uid, val in all_values:
                member = server.get_member(uid)
                if member == None: continue
                member_vals.append((member, val))
        
        else:
            title += f"(Global)"
            for uid, val in all_values:
                member = self.bot.get_user(uid)
                if member == None: continue
                member_vals.append((member, val))
        
        for i in range(len(member_vals)):
            if i > 19:
                if author_data != None: break
                continue
            member, val = member_vals[i]
            top20 += f"{i + 1}. {member.display_name} - **{val}**\n"
            if member.id == author.id: author_data = f"-# Your Positon: {ordinal(i + 1)} (score: {val})."
        
        if author_data != None: top20 += author_data
        embed = discord.Embed(
            description=top20,
            timestamp=datetime.now(),
            color=0x2ECC71
        )
        embed.set_author(name=title, icon_url=icon)
        timer.end()
        embed.set_footer(text=f"{timer.elapsed}ms")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(stats(bot))