import discord
import random
import banned_words
import banned_users

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from log import log_message
from discord.ui import Modal, TextInput

class botcommands(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
        self.say_ctx_menu = app_commands.ContextMenu(name="Say", callback=self.say_menu_callback)
        self.bot.tree.add_command(self.say_ctx_menu)
    
    async def cog_unload(self):
        self.bot.tree.remove_command(self.say_ctx_menu.name, type=self.say_ctx_menu.type)
    
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
            f"Chat, what should I tell {username}?",
            "The great oracle foresees..."
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
            "GTA6 delayed.",
            "Good luck.",
            "You will destroy your opponent.",
            "GEM ALARM",
            "Someone will steal your bike.",
            "IMG_1124.jpeg",
            f"{username} will never be a wizard",
            "Fuck you"
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
    
    @commands.hybrid_command(name="changelog", description="Get the bot's changelog")
    async def changelog(self, ctx:commands.Context):
        try:
            with open("README.txt", 'r', encoding='utf-8') as file:
                content = file.read()
                
                if len(content) > 1900:
                    await ctx.send(file=discord.File("README.txt"))
                
                else:
                    await ctx.send(f"```\n{content}\n```")
        
        except FileNotFoundError:
            await ctx.send("Sorry, the changelog is missing.")
        
        except Exception as e:
            await ctx.send(f"Error reading changelog: {e}")

    @commands.command(name="secret_dev_command", aliases=["dev"])
    async def dev_command(self, ctx:commands.Context):
        if ctx.author.id != 554775854501330956:
            return await ctx.send("fuck you lmao")
        
        bot_guilds = list(self.bot.guilds)
        guild_str = "**Bot Guilds:**\n"
        
        for guild in bot_guilds:
            guild_str += f"> {guild}\n"

        return await ctx.send(guild_str)
    
    @commands.hybrid_command(name="say", description="Make IShowWizardry say something. (Slurs aren't allowed btw)", aliases=["s"])
    async def say(self, ctx:commands.Context, message:str):
        if not message:
            return
        
        user = ctx.author
        
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        
        bannedusers = banned_users.BannedUsers()
        timestamp = bannedusers.get_timestamp(user.id)
        
        if bannedusers.check_user(user.id) and timestamp != None:
            return await ctx.send(f"You've been banned from using this command until {timestamp}", ephemeral=True)
        
        if ctx.interaction:
            await ctx.send("Message sent!", ephemeral=True, delete_after=1)
        
        else:
            await ctx.message.delete()
        
        banned = banned_words.BannedWords()
        banned.disable_tier(2)
        banned.disable_tier(3)
        banned.disable_tier(4)
        
        msg_words = message.split(" ")
        channel = ctx.channel
        
        await log_message(user=user, message=message, iso_time=datetime.now().isoformat(), bot=self.bot, command_used="/say", server=ctx.guild)
        
        for word in msg_words:
            if banned.isprofane(word):
                return await user.send(f"The word '{word}' is not permitted.")
        
        await channel.send(message)
    
    async def say_menu_callback(self, interaction:discord.Interaction, message:discord.Message):
        await interaction.response.send_modal(say_modal(message, self.bot))
        
class say_modal(Modal, title="Reply to a message"):
    def __init__(self, message:discord.Message, bot:commands.Bot):
        super().__init__()
        self.message = message
        self.bot = bot
        
        self.reply = TextInput(
            label="What do you want to say?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.reply)
    
    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        
        bannedusers = banned_users.BannedUsers()
        timestamp = bannedusers.get_timestamp(user.id)
        
        if bannedusers.check_user(user.id) and timestamp != None:
            return await interaction.response.send_message(f"You've been banned from using this command until {timestamp}", ephemeral=True)
        
        banned = banned_words.BannedWords()
        banned.disable_tier(2)
        banned.disable_tier(3)
        banned.disable_tier(4)
        
        reply = f"{self.reply}"
        reply_words = reply.split(" ")
        
        await log_message(user=user, message=reply, iso_time=datetime.now().isoformat(), bot=self.bot, command_used="Say menu cmd", server=interaction.guild)
        
        for word in reply_words:
            if banned.isprofane(word):
                return await user.send(f"The word '{word}' is not permitted.")
        
        await self.message.reply(reply)
        await interaction.response.send_message("Reply sent!", ephemeral=True, delete_after=1)

async def setup(bot):
    await bot.add_cog(botcommands(bot))