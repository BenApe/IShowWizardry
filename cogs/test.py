# This file is a demonstration of how buttons and view objects work

import discord

from discord.ext import commands
from discord.ui import Button, View

class test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="test_embed", description="ignore")
    async def test_embed(self, ctx:commands.Context, message:str):
        timeout = 1000                                     # After 1000s you won't be able to interact with the buttons anymore
        
        view = test_view(message=message, timeout=timeout) # Create a view object
        embed = await view.update_embed()                  # Get the embed from the view object
        await ctx.send(embed=embed, view=view)             # Send the embed
    
class test_view(View):
    def __init__(self, message:str, timeout:int):
        super().__init__(timeout=timeout)   # This is necessary but you don't need to define a timeout
        self.message = message
    
    # There are two ways to add a button to an embed:
    # 1. Create a button callback function and add it to the view object
    #   - This allows you to change what buttons are actually attached to the embed
    #   - You need to manually add the button to the embed
    #
    # 2. Directly create the button
    #   - Buttons made this way cant be easily changed
    #   - Buttons made this way are automatically added to the embed
    
    async def update_embed(self, interaction:discord.Interaction = None, add_button:bool = False, remove_buttons:bool = False):
        embed = discord.Embed(
            title="This is an embed!",
            description=self.message
        )
        
        if add_button:
            new_button = Button(label=self.message, style=discord.ButtonStyle.blurple)  # Creates a button
            new_button.callback = self.button_callback                                  # Sets the button's callback (what it actually does)
            self.add_item(new_button)                                                   # Adds the button to the view object, which is then attached to the embed
        
        elif remove_buttons:
            embed = discord.Embed(
                title="This is an embed!",
                description=f"{self.message}\n\n**Buttons removed**"
            )
            self.clear_items()  # Removes all buttons from the embed
        
        if interaction:
            await interaction.response.edit_message(embed=embed, view=self) # If this function was called because of a button press, edit the original embed
        
        else:
            remove_button = Button(label="Remove all buttons", style=discord.ButtonStyle.red)   # This is all the same as the previous button, but I put it here so it would only get
            remove_button.callback = self.remove_callback                                       # added if the function wasn't called by a button press
            self.add_item(remove_button)
            
            return embed    # If this function wasn't called by a button press, just return the embed
    
    async def button_callback(self, interaction:discord.Interaction):   # This is the button added in the "add_button" if-statement
        await interaction.response.send_message("Button pressed!")      # Pressing this button will respond with "Button pressed!"
    
    async def remove_callback(self, interaction:discord.Interaction):                           # This is the remove_button from before
        await self.update_embed(interaction=interaction, add_button=False, remove_buttons=True) # The interaction is sent into the update_embed function so it can edit the original message
    
    # This is method 2:
    @discord.ui.button(label="Add Button", style=discord.ButtonStyle.green)                     # Rather than defining the button and adding it manually like before, you can define everything like this
    async def add_button(self, interaction:discord.Interaction, button:Button):                 # Now you have to add the "button:Button" parameter
        await self.update_embed(interaction=interaction, add_button=True, remove_buttons=False)
    
    # Extra note since I didn't have space:
    # Buttons can have a few different styles, but they mostly just change the color of the button.
    # URL/Link are exceptions, and I don't really know what they do because I've never had to use them

async def setup(bot):
    await bot.add_cog(test(bot))