VERSION = "0.2.0"

import discord
import json
import os
import asyncio

from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands

load_dotenv(dotenv_path=".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True
prefixes = ['cast ', 'Cast ', 'CAST ', '~']
bot = commands.Bot(command_prefix=prefixes, intents=intents)

debug_mode = input("Debug mode? (y/n) ") == "y"

banner = rf'''
 *      *     *    *          *        *     *           *       *   
   *___ ____*_         *      __ *__ __           *        _*       *
   /  //___///    *       *  / / / //_/__  *   *          //         
 * // //__ //__ ____*______ / /─/ /__\__ \ ___   ____*___//____ _* _ 
  // ___///∙¬ // , // / / // / / // // __// _ \ / ,_// _ // ,_// / / 
/__//___/// ///___//_____//_____//_/ \___\\__///_/  /___//_/   \_ /  
________________________________________________________________//   
\_/Version {VERSION}\_____________________________/Made by: mega05\_/    
'''

# Initialize
@bot.event
async def on_ready():
    extentions = [
        "cogs.botcommands",
        "cogs.duel",
        "cogs.fish",
        "cogs.dice",
        "cogs.test",
        "cogs.levels"
    ]
    
    print("Jello World!")
    
    for ext in extentions:
        try:
            await bot.load_extension(ext)
        except commands.ExtensionError as e:
            print(f"Failed to load extension {ext}: {e}")
            
    try:
        synced = await bot.tree.sync()
        
        print(f"Synced {len(synced)} command(s)")
        print(banner)
        
        activity = discord.Activity(type=discord.ActivityType.watching, name="the orb")
        await bot.change_presence(status=discord.Status.online, activity=activity)
    except Exception as e:
        print(e)

    if debug_mode:
        print(f"\nBot prefix: '{bot.command_prefix}'")
        
        print(f"\nPrefix commands ({len(bot.commands)}):")
        for cmd in bot.commands:
            print(f"- {cmd.name}")
        
        print(f"\nSlash Commands ({len(bot.tree.get_commands())}):")
        for cmd in bot.tree.get_commands():
            print(f"- {cmd.name}")

if not debug_mode:
    @bot.event
    async def on_command_error(ctx, error):
        print(f"Command error: {error}")
        # await ctx.reply(f"Command error: {error}", ephemeral=True)

    @bot.event
    async def on_error(event):
        print(f"Error: {event}")

bot.run(BOT_TOKEN)