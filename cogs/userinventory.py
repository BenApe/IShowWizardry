import discord
import response

from discord.ext import commands
from discord.ui import Button, View
from botutils import savejson, loadjson

class userinventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="inventory", description="View your inventory", aliases=["inv", "i"])
    async def inventory(self, ctx:commands.Context, page:str = "home"):
        user = ctx.author
        
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        
        page_list = ["home", "spells", "fish"]
        page = page.lower()
        
        if page not in page_list:
            pages = ""
            
            for name in page_list:
                pages += f"'{name}', "
            
            return await ctx.send(f"Inventory page '{page}' not found! Valid pages: {pages[:-2]}", ephemeral=True)
        
        view = invView(ctx, user, page=page)
        embed = await view.update_embed()
        await ctx.send(embed=embed, view=view)

class invView(View):
    def __init__(self, ctx:commands.Context, user:discord.User, page:str):
        super().__init__()
        self.ctx = ctx
        self.user = user
        self.user_id = user.id
        self.page = page
    
    def get_home_embed(self):
        embed = discord.Embed(
            description="🚧Under Construction🚧",
            color=0xcc64f9
        )
        embed.set_author(name=f"{self.ctx.author.display_name}'s Inventory", icon_url=self.ctx.author.display_avatar)
        embed.set_footer(text="Page: Homepage")
        
        return embed
    
    def get_spells_embed(self):
        embed = discord.Embed(
            description="🚧Under Construction🚧",
            color=0xcc64f9
        )
        embed.set_author(name=f"{self.ctx.author.display_name}'s Inventory", icon_url=self.ctx.author.display_avatar)
        embed.set_footer(text="Page: Spells")
        
        return embed
    
    def get_fish_embed(self):
        fish_path = f"user_data/fish/{self.user_id}"
        user_fish = loadjson(fish_path)
        
        fishes = ""
        
        for fish in user_fish:
            fishyfishy = user_fish.get(fish)
            name = fishyfishy.get("name")
            rarity = fishyfishy.get("rarity")
            size = fishyfishy.get("size")
            value = fishyfishy.get("value")
            
            fishes += f"**{name} ({value} Mana)**\n> Rarity: {rarity}\n> Size: {size}\n-# `ID: {fish}`\n\n"
        
        fishes = "You don't have any fish! use `/fishing_rod` to catch some fish." if fishes == "" else fishes
    
        embed = discord.Embed(
            description=fishes,
            color=0xcc64f9
        )
        embed.set_author(name=f"{self.ctx.author.display_name}'s Inventory", icon_url=self.ctx.author.display_avatar)
        embed.set_footer(text="Page: Fish")
        
        return embed
    
    async def update_embed(self, interaction:discord.Interaction = None):
        embed = None
        
        if self.page == "home":
            embed = self.get_home_embed()
            self.clear_items()
            
            spells_btn = Button(label="Spells", style=discord.ButtonStyle.blurple)
            spells_btn.callback = self.spells_callback
            self.add_item(spells_btn)
            
            fish_btn = Button(label="Fish", style=discord.ButtonStyle.blurple)
            fish_btn.callback = self.fish_callback
            self.add_item(fish_btn)
            
            refresh_btn = Button(label="🔄️", style=discord.ButtonStyle.gray)
            refresh_btn.callback = self.refresh_callback
            self.add_item(refresh_btn)
        
        elif self.page == "spells":
            embed = self.get_spells_embed()
            self.clear_items()
            
            home_btn = Button(emoji="🏠", style=discord.ButtonStyle.gray)
            home_btn.callback = self.home_callback
            self.add_item(home_btn)
            
            refresh_btn = Button(label="🔄️", style=discord.ButtonStyle.gray)
            refresh_btn.callback = self.refresh_callback
            self.add_item(refresh_btn)
        
        elif self.page == "fish":
            embed = self.get_fish_embed()
            self.clear_items()
            
            home_btn = Button(emoji="🏠", style=discord.ButtonStyle.gray)
            home_btn.callback = self.home_callback
            self.add_item(home_btn)
            
            refresh_btn = Button(label="🔄️", style=discord.ButtonStyle.gray)
            refresh_btn.callback = self.refresh_callback
            self.add_item(refresh_btn)
        
        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        
        else:
            return embed
    
    async def spells_callback(self, interaction:discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        self.page = "spells"
        await self.update_embed(interaction=interaction)
    
    async def fish_callback(self, interaction:discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        self.page = "fish"
        await self.update_embed(interaction=interaction)
    
    async def home_callback(self, interaction:discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        self.page = "home"
        await self.update_embed(interaction=interaction)
    
    async def refresh_callback(self, interaction:discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(response.wrong_press().response, ephemeral=True)
        
        await self.update_embed(interaction=interaction)
    
async def setup(bot):
    await bot.add_cog(userinventory(bot))