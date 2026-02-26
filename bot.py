VERSION = "0.2.2"

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
bot = commands.Bot(command_prefix=prefixes, intents=intents, help_command=None)

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

@bot.hybrid_command(name="help", aliases=["h", "commands"], description="Shows a list of commands and other useful information.")
async def help(ctx:commands.Context, command_name:str=None):
    command_descriptions = {
        "General":{
            "help": "Shows this message. You can also specify a command to get its description. Aliases: 'h', 'commands'",
            "ping": "Check the bot's latency.",
            "changelog": "See what has changed in the most recent update. May not be accurate."
        },
        "Fun":{
            "die": "Roll a die with as many sides as you want.",
            "fishing_rod": "Go fishing! Currently, the bot doesn't store the fish you collect, but you can still gain xp. Aliases: 'fish', 'fishingrod'",
            "fish_pool": "Check how many fish you have in your pond. Aliases: 'pool', 'pond'",
            "ponder": "Have your fortune read."
        },
        "Levels & XP":{
            "level": "Get your Wizard Level.",
            "edit_level": "MOD ONLY - Edit a user's level or xp amount. Changing level will set xp to the minimum for that level."
        }
    }
    
    if command_name == None:
        help_description = ""
        
        for section in command_descriptions:
            help_description += f"### {section}\n"
            section_cmds = command_descriptions.get(section)
            
            for command in section_cmds:
                help_description += f"- **{command}:**"
                cmd_description = section_cmds.get(command)
                help_description += f" {cmd_description}\n"
        
        embed = discord.Embed(
            description=help_description
        )
        
        prefix_str = ""
        
        for prefix in prefixes:
            prefix_str += f"'{prefix.split(" ")[0]}', "
            
        prefix_str = prefix_str[:-2]
        
        embed.set_author(name=f"IShowWizardry v{VERSION}", icon_url="https://cdn.discordapp.com/avatars/1470289312997310516/1da0eec450e33ba919bd9e03cd758f92.webp?size=1024")
        embed.set_footer(text=f"Prefixes: {prefix_str}")
        
        await ctx.send(embed=embed)
    
    else:
        cmd_description = ""
        
        for section_name in command_descriptions:
            section = command_descriptions.get(section_name)
            if command_name in section:
                cmd_description = section.get(command_name)
                break
        
        embed = discord.Embed(
            title=f"Command: {command_name}",
            description=cmd_description
        )
        
        prefix_str = ""
        
        for prefix in prefixes:
            prefix_str += f"'{prefix.split(" ")[0]}', "
            
        prefix_str = prefix_str[:-2]
        
        embed.set_author(name=f"IShowWizardry v{VERSION}", icon_url="https://cdn.discordapp.com/avatars/1470289312997310516/1da0eec450e33ba919bd9e03cd758f92.webp?size=1024")
        embed.set_footer(text=f"Prefixes: {prefix_str}")
        
        await ctx.send(embed=embed)

bot.run(BOT_TOKEN)