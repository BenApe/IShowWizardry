import discord
import random
import response
import spell
import spellbook
import spellcaster

from botutils import loadjson
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
        embed = await view.update_embed()
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="library", description="Open the Wizard's library")
    async def library(self, ctx:commands.Context):
        view = library_view(ctx)
        embed = view.update_embed()
        await ctx.send(embed=embed, view=view)

class duel_view(View):
    def __init__(self, ctx:commands.Context, player_1:discord.User, player_2:discord.User):
        super().__init__()
        self.ctx = ctx
        self.player_1 = player_1
        self.player_2 = player_2
        self.p1_ready = False
        self.p2_ready = False
        self.p1_spellbook = spellbook.spellbook(self.player_1)
        self.p2_spellbook = spellbook.spellbook(self.player_2)
        self.p1_spells = self.p1_spellbook.get_spells(as_dict=False)
        self.p2_spells = self.p2_spellbook.get_spells(as_dict=False)
    
    async def update_embed(self, interaction:discord.Interaction = None):
        p1_name = self.player_1.display_name
        p2_name = self.player_2.display_name
        
        if not self.p1_ready and not self.p2_ready:
            embed = discord.Embed(title="*Wizard Duel*",
                                description="🚧Under Construction🚧",
                                color=0xcc64f9)
            embed.set_author(name=f"{p1_name} vs. {p2_name}")
            self.clear_items()
            
            ready_btn = Button(label="Ready", style=discord.ButtonStyle.green)
            ready_btn.callback = self.ready_callback
            self.add_item(ready_btn)
            
            prepare_btn = Button(label="Prepare Spells", style=discord.ButtonStyle.blurple, disabled=True)
            prepare_btn.callback = self.prepare_spells_callback
            self.add_item(prepare_btn)
        
        elif self.p1_ready != self.p2_ready:
            player = self.player_1 if self.p1_ready else self.player_2
            
            embed = discord.Embed(title="*Wizard Duel*",
                                description=f"{player.display_name} is ready!",
                                color=0xcc64f9)
            embed.set_author(name=f"{p1_name} vs. {p2_name}")
            self.clear_items()
            
            ready_btn = Button(label="Ready", style=discord.ButtonStyle.green)
            ready_btn.callback = self.ready_callback
            self.add_item(ready_btn)
            
            prepare_btn = Button(label="Prepare Spells", style=discord.ButtonStyle.blurple, disabled=True)
            prepare_btn.callback = self.prepare_spells_callback
            self.add_item(prepare_btn)
        
        elif self.p1_ready and self.p2_ready:
            embed = discord.Embed(title="*Wizard Duel*", color=0xcc64f9)
            embed.set_author(name=f"{p1_name} vs. {p2_name}")
            embed.add_field(
                name=f"{p1_name}",
                value="player 1 stuff goes here",
                inline=True
            )
            embed.add_field(
                name=f"{p2_name}",
                value="player 2 stuff goes here",
                inline=True
            )
            self.clear_items()
            
            cast_btn = Button(label="Cast Spell", style=discord.ButtonStyle.green)
            cast_btn.callback = self.cast_spells_callback
            self.add_item(cast_btn)
            
        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            return embed
    
    async def ready_callback(self, interaction:discord.Interaction):
        if interaction.user == self.player_1:
            self.p1_ready = True
        elif interaction.user == self.player_2:
            self.p2_ready = True
        else:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        await self.update_embed(interaction=interaction)
        # await interaction.response.send_message(f"{interaction.user.mention} is ready!")
    
    async def prepare_spells_callback(self, interaction:discord.Interaction):
        return await interaction.response.send_message("This button is under construction!")
    
    async def cast_spells_callback(self, interaction:discord.Interaction):
        if interaction.user == self.player_1:
            embed = discord.Embed(title="Your Prepared Spells")
            view = cast_spell_view(self.p1_spellbook)
            
            for item in self.p2_spells:
                user_spell = f"```\n{item.to_string()}\n```"
                embed.add_field(name=" ", value=user_spell, inline=False)
            
            view.add_buttons()
            return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        elif interaction.user == self.player_2:
            embed = discord.Embed(title="Your Prepared Spells")
            view = cast_spell_view(self.p2_spellbook)
            
            for item in self.p2_spells:
                user_spell = f"```\n{item.to_string()}\n```"
                embed.add_field(name=" ", value=user_spell, inline=False)
            
            view.add_buttons()
            return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)

class cast_spell_view(View):
    def __init__(self, user_spellbook:spellbook.spellbook):
        super().__init__()
        self.user_spellbook = user_spellbook
        self.user_spells = self.user_spellbook.get_spells(as_dict=False)
        
    def add_buttons(self):
        btn1 = Button(label=f"Cast {self.user_spells[0].name}", style=discord.ButtonStyle.blurple)
        btn1.callback = self.btn1_callback
        self.add_item(btn1)
        
        btn2 = Button(label=f"Cast {self.user_spells[1].name}", style=discord.ButtonStyle.blurple)
        btn2.callback = self.btn2_callback
        self.add_item(btn2)
        
        btn3 = Button(label=f"Cast {self.user_spells[2].name}", style=discord.ButtonStyle.blurple)
        btn3.callback = self.btn3_callback
        self.add_item(btn3)
        
        btn4 = Button(label=f"Cast {self.user_spells[3].name}", style=discord.ButtonStyle.blurple)
        btn4.callback = self.btn4_callback
        self.add_item(btn4)
    
    async def btn1_callback(self, interaction:discord.Interaction):
        if interaction.user != self.user_spellbook.owner:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)

        return await interaction.response.send_message("test")
    
    async def btn2_callback(self, interaction:discord.Interaction):
        if interaction.user != self.user_spellbook.owner:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)

        return await interaction.response.send_message("test")
    
    async def btn3_callback(self, interaction:discord.Interaction):
        if interaction.user != self.user_spellbook.owner:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)

        return await interaction.response.send_message("test")
    
    async def btn4_callback(self, interaction:discord.Interaction):
        if interaction.user != self.user_spellbook.owner:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)

        return await interaction.response.send_message("test")

class library_view(View):
    def __init__(self, ctx:commands.Context):
        super().__init__()
        self.ctx = ctx
        
        self.built_in_spells = loadjson("bot_data/built_in_spells")
    
    def update_embed(self):
        embed = discord.Embed(title="The Library (doesn't do anything yet)",
                      description="Welcome to the Wizard's library!\n\n**Learn spells:** Spend your mana to learn new spells. Options change every 8 hours.\n\n**Spellbook:** View your spells.\n\n**Upgrade Spells:** Upgrade your spells. (Level 5 required)\n\n**Create Spells:** Create new spells. (Level 10 required)",
                      colour=0x00b0f4)
        
        return embed
    
    @discord.ui.button(label="Learn Spells", style=discord.ButtonStyle.green)
    async def learn_spells(self, interaction:discord.Interaction, button:Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        await interaction.response.send_message("This command is still under construction.", ephemeral=True)
        
    @discord.ui.button(label="Spellbook", style=discord.ButtonStyle.green)
    async def spellbook(self, interaction:discord.Interaction, button:Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        await interaction.response.send_message("This command is still under construction.", ephemeral=True)
    
    @discord.ui.button(label="Upgrade Spells", style=discord.ButtonStyle.green)
    async def upgrade_spells(self, interaction:discord.Interaction, button:Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        await interaction.response.send_message("This command is still under construction.", ephemeral=True)
    
    @discord.ui.button(label="Create Spells", style=discord.ButtonStyle.green)
    async def create_spells(self, interaction:discord.Interaction, button:Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        await interaction.response.send_message("This command is still under construction.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(duel(bot))