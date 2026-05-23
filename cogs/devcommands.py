import discord

from discord import app_commands
from discord.ext import commands
from userstats import userstats
from botutils import grab_filenames, loadjson, process_timer

class devcmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="guild_list")
    @commands.is_owner()
    async def guild_list(self, ctx:commands.Context):
        guilds = list(self.bot.guilds)
        guild_str = "**Bot Guilds:**\n"
        
        for guild in guilds:
            guild_str += f"> {guild}\n"
        
        await ctx.send(guild_str)
    
    @commands.command(name="verify_stats")
    @commands.is_owner()
    async def verify_stats(self, ctx:commands.Context):
        timer = process_timer()
        starboards = grab_filenames("server_data/starboard")
        all_users = []
        fetches = 0
        fails = 0
        for server_id in starboards:
            board = loadjson(server_id[:-5])
            for msg_id, data in board.items():
                if msg_id == 0: continue
                rxn_ct = data.get("rxn_ct")
                channel = self.bot.get_channel(data.get("chnl"))
                try:
                    message = await channel.fetch_message(msg_id)
                    user = message.author
                    all_users.append((user.id, rxn_ct))
                    fetches += 1
                except:
                    fails += 1
                    continue
        
        user_changes = {}
        for uid, rct in all_users:
            msgs = 1
            if uid in user_changes.keys():
                user_data = user_changes.get(uid)
                msgs += user_data.get("msgs")
                rct += user_data.get("rct")
            user_changes.update({
                    uid: {
                        "msgs": msgs,
                        "rct": rct
            }})
        
        for uid, data in user_changes.items():
            print(uid, data)
            statsuser = userstats(uid)
            statsuser.update_value(value="stars_recieved", set=data.get("rct"))
            statsuser.update_value(value="board_msgs", set=data.get("msgs"))
        
        timer.end()
        await ctx.send(f"Checked {fetches + fails} messages and updated starboard data for {len(user_changes)} users.\n-# Failed to fetch {fails} messages. Took {timer.elapsed}ms.")

async def setup(bot: commands.Bot):
    await bot.add_cog(devcmds(bot))