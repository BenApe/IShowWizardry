import discord
import random

from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

class duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="wizard_duel", description="Start a wizard duel with someone")
    async def wizard_duel(self, ctx:commands.Context, opponent:discord.User):
        player_1 = ctx.author
        
        if isinstance(ctx, discord.Interaction):
            player_1 = ctx.user
        
        view = duel_view(ctx, player_1, opponent)
        embed = view.update_embed()
        await ctx.send(embed=embed, view=view)

class duel_view(View):
    def __init__(self, ctx:commands.Context, player_1:discord.User, player_2:discord.User):
        super().__init__()
        self.ctx = ctx
        self.player_1 = player_1
        self.player_2 = player_2
    
    def update_embed(self):
        p1_name = self.player_1.display_name
        p2_name = self.player_2.display_name
        
        embed = discord.Embed(title="*Wizard Duel*",
                              description="🚧Under Construction🚧",
                              color=0xcc64f9)
        
        embed.set_author(name=f"{p1_name} vs. {p2_name}")
        
        return embed

async def setup(bot):
    await bot.add_cog(duel(bot))