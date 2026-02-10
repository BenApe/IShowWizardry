import discord
import random

from discord.ext import commands
from discord import app_commands

class botcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ponder", description="Ponder")
    async def ponder(self, ctx:commands.Context):
        user = ctx.author
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        
        username = user.mention
        
        ponderings = [
            "My orb scrys an uncertain future...",
            "I forsee an evil apparition in your future...",
            "A storm is brewing...",
            "The gods speak to me...",
            f"@grok show me {username}'s future\n\ngrok:",
            "I think...",
            "<@801288893244506162> thoughts?",
            f"MageGPT, generate a future that {username} will love!\n\nAccessing tomes of ancient knowledge...\n\nDivining alternate timelines...\n\nYour future is:",
            "/react...",
            "*Casting divination spell...*",
            "",
            "My name is IShowWizardry.",
            "Did you know?",
            "Dude the orb literally said",
            "Im recieving a message from the spirits...",
            "The vision is unclear...",
            f"Chat, what should I tell {username}?"
        ]
        
        postponderings = [
            "You will not survive.",
            "Your death imminent.",
            "Nothing will happen.",
            "Your fate is sealed.",
            "There will be great hardship.",
            "IShowFinance will not prevail.",
            "Hahahaha im an evil ass wizard",
            "#epicness",
            "You will lose all of your belongings.",
            "lmao",
            "You will find 1 million gold.",
            "You will die in a wizard duel.",
            "",
            "W SPEED",
            "ASMRSpeed's life will be cut short.",
            "I forgot",
            "You will be slain by a beast.",
            "Your quest will succeed.",
            "*Casts lightning spell at you*",
            "GTA6 delayed."
        ]
        
        full_ponder = random.choice(ponderings) + " " + random.choice(postponderings)
        
        await ctx.reply(full_ponder)
    
    @commands.hybrid_command(name="ping", description="Check IShowWizardry's latency")
    async def ping(self, ctx:commands.Context):
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** `{latency}ms`",
            color=0x43ea10
        )
        
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(botcommands(bot))