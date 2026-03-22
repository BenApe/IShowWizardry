import discord
import os

from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime
from botutils import savejson, loadjson
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
LOG_CHANNEL_ID = os.getenv("REPORT_CHANNEL_ID")
DEV_ID = os.getenv("DEV_ID")

class bug_report(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="bug_report", description="Submit a bug report to the dev.")
    @app_commands.checks.cooldown(1, 300)
    async def bug_report(self, interaction:discord.Interaction):
        blacklist = loadjson(file_name="bot_data/bug_report_blacklist")
        user_ids = list(blacklist.keys())
        
        if interaction.user.id in user_ids:
            reason = blacklist.get(interaction.user.id)
            return await interaction.response.send_message(f"You have been banned from sending in bug reports. Reason:\n> {reason}", ephemeral=True)

        await interaction.response.send_modal(bug_modal(interaction, self.bot))
    
    @bug_report.error
    async def report_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Command is on cooldown. Try again in {error.retry_after:.1f}s.", ephemeral=True)

class bug_modal(Modal, title="Submit a bug report"):
    def __init__(self, original_interaction:discord.Interaction, bot:commands.Bot):
        super().__init__()
        self.original_interaction = original_interaction
        self.bot = bot
        
        self.command = TextInput(
            label="What command did you use?",
            style=discord.TextStyle.short,
            placeholder="Leave blank if the issue doesn't relate to a command",
            required=False
        )
        self.add_item(self.command)
        
        self.report_msg = TextInput(
            label="Describe what happened",
            style=discord.TextStyle.paragraph,
            placeholder="Include all relevant context",
            required=True,
            min_length=1,
            max_length=4000
        )
        self.add_item(self.report_msg)
    
    async def on_submit(self, interaction: discord.Interaction):
        channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
        now = int(datetime.now().timestamp())
        timestamp = f"<t:{now}:f>"
        user = interaction.user
        user_id = interaction.user.id
        server = interaction.guild
        bug_reports = loadjson("bot_data/bug_reports")
        report_id = bug_reports.get(-1) or 1
        cmd_str = f"{self.command}"
        msg_str = f"{self.report_msg}"
        desc = ""
        response_msg = "Bug report sent to the dev! Thanks!\n-# Note: You must have DM's open if you want the dev to respond."
        
        # Dev only commands
        dev_commands = ["$(access)", "$(remove_blacklist)", "$(list)", "$(blacklist)", "$(user_info)", "$(help)"]
        if interaction.user.id == DEV_ID and cmd_str in dev_commands:
            if cmd_str == "$(access)":
                try:
                    report_id = int(msg_str)
                    report = bug_reports.get(report_id)
                    user_id = report.get("user")
                    cmd_str = report.get("cmd")
                    msg_str = report.get("msg")
                    now = report.get("timestamp")
                    timestamp = f"<t:{now}:f>"
                    response_msg = f"Accessed report ID `{report_id}`"
                except:
                    return await interaction.response.send_message(f"Report ID `{msg_str}` incorrect or missing.", ephemeral=True)
            
            elif cmd_str == "$(remove_blacklist)":
                blacklist = loadjson("bot_data/bug_report_blacklist")
                try:
                    user_id = int(msg_str)
                    reason = blacklist.get(user_id)
                    blacklist.pop(user_id)
                    savejson("bot_data/bug_report_blacklist", blacklist)
                    user = await self.bot.fetch_user(user_id)
                    return await interaction.response.send_message(f"User {user.name} ({user_id}) removed from blacklist. Original reason:\n> {reason}")
                except:
                    return await interaction.response.send_message(f"User ID `{msg_str}` incorrect or missing.", ephemeral=True)
            
            elif cmd_str == "$(list)":
                return await interaction.response.send_message(file=discord.File("bot_data/bug_reports.json"))
            
            elif cmd_str == "$(blacklist)":
                return await interaction.response.send_message(file=discord.File("bot_data/bug_report_blacklist.json"))
            
            elif cmd_str == "$(user_info)":
                blacklist = loadjson("bot_data/bug_report_blacklist")
                try:
                    user_id = int(msg_str)
                    user = await self.bot.fetch_user(user_id)
                    desc = f"User ID: {user_id}"
                    
                    if user_id in blacklist:
                        reason = blacklist.get(user_id)
                        desc += f"\nUser blacklisted. Reason:\n> {reason}"
                    
                    else:
                        desc += "\n**Bug Reports:** \n"
                        
                        for report_id in bug_reports:
                            if report_id == -1:
                                continue
                            
                            report = bug_reports.get(report_id)
                            reporter_id = report.get("user")
                            
                            if reporter_id == user_id:
                                desc += f"{report_id}, "
                        
                        desc = desc[:-2]
                    
                    embed = discord.Embed(description=desc)
                    embed.set_author(name=f"User Info for {user.name}", icon_url=user.avatar.url)
                    
                    return await interaction.response.send_message(embed=embed)
                except:
                    return await interaction.response.send_message(f"User ID `{msg_str}` incorrect or missing.", ephemeral=True)
            
            elif cmd_str == "$(help)":
                for cmd in dev_commands:
                    desc += f"{cmd}, "
                
                desc = desc[:-2]
                return await interaction.response.send_message(desc, ephemeral=True)
        
        else:
            bug_reports.update({-1: report_id + 1})
        
        if cmd_str == "":
            desc = msg_str
            bug_reports.update({report_id: {"user": user_id, "cmd": "None", "msg": f"{msg_str}", "timestamp": now}})
        else:
            desc = f"**Command used:**\n{cmd_str}\n**Bug report:**\n{msg_str}"
            bug_reports.update({report_id: {"user": user_id, "cmd": f"{cmd_str}", "msg": f"{msg_str}", "timestamp": now}})
        
        savejson("bot_data/bug_reports", data=bug_reports)
        
        embed = discord.Embed(
            description=desc,
            timestamp=datetime.now()
        )
        
        embed.set_author(name=f"Bug report submitted by {user.name} ({user.id})", icon_url=user.avatar.url)
        embed.set_footer(text=f"ID: {report_id} | From: {server.name} ({server.id})")
        
        view = bug_view(user=user, report_desc=desc, timestamp=timestamp, report_id=report_id)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(response_msg, ephemeral=True)

class bug_view(View):
    def __init__(self, user:discord.User, report_desc:str, timestamp:str, report_id:int):
        super().__init__()
        self.user = user
        self.report_desc = report_desc
        self.timestamp = timestamp
        self.report_id = report_id
        
    async def send_response(self, message:str, interaction:discord.Interaction, resolved:bool = False):
        title = "The Developer has responded to your bug report:"
        
        if resolved:
            title = "The developer has resolved your issue:"
            try:
                bug_reports = loadjson("bot_data/bug_reports")
                bug_reports.pop(self.report_id)
                savejson("bot_data/bug_reports", bug_reports)
            except Exception as e:
                return await interaction.followup.send(f"An error occurred while trying to resolve bug report: {e}", ephemeral=True)
        
        embed = discord.Embed(
            title=title,
            description=message,
            timestamp=datetime.now()
        )
            
        embed.add_field(
            name="__Original Report:__",
            value=f"{self.report_desc}\n-# Submitted {self.timestamp}"
        )
        
        try:
            await self.user.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(f"Unable to DM {self.user.name} ({self.user.id}). User may have DM's disabled.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)
    
    async def blacklist_user(self, reason:str, interaction:discord.Interaction):
        blacklist = loadjson("bot_data/bug_report_blacklist")
        blacklist.update({self.user.id: reason})
        savejson("bot_data/bug_report_blacklist", blacklist)
        
        reports = loadjson("bot_data/bug_reports")
        user_reports = []
        
        for report_id in reports:
            if report_id == -1:
                continue
            
            report = reports.get(report_id)
            user_id = report.get("user")
            if user_id == self.user.id:
                user_reports.append(report_id)
        
        for report_id in user_reports:
            reports.pop(report_id)
        
        savejson("bot_data/bug_reports", reports)
        
        await interaction.response.send_message(f"User {self.user.name} ({self.user.id}) added to blacklist. Reason:\n> {reason}")
    
    @discord.ui.button(label="Respond", style=discord.ButtonStyle.blurple)
    async def respond_btn(self, interaction:discord.Interaction, button:Button):
        await interaction.response.send_modal(response_modal(self))
    
    @discord.ui.button(label="Resolve", style=discord.ButtonStyle.green)
    async def resolve_btn(self, interaction:discord.Interaction, button:Button):
        await interaction.response.send_modal(response_modal(self, True))

    @discord.ui.button(label="Blacklist User", style=discord.ButtonStyle.red)
    async def blacklist_btn(self, interaction:discord.Interaction, button:Button):
        await interaction.response.send_modal(blacklist_modal(self))
    
class response_modal(Modal, title="Respond to a bug report"):
    def __init__(self, view:bug_view, resolved:bool = False):
        super().__init__()
        self.view = view
        self.resolved = resolved
        
        self.response = TextInput(
            label="Response",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.response)
    
    async def on_submit(self, interaction:discord.Interaction):
        await self.view.send_response(message=f"{self.response}", interaction=interaction, resolved=self.resolved)
        await interaction.response.send_message(f"### Response sent to user:\n{self.response}")

class blacklist_modal(Modal, title="Blacklist a user"):
    def __init__(self, view:bug_view):
        super().__init__()
        self.view = view
        
        self.reason = TextInput(
            label="Reason for blacklist",
            style=discord.TextStyle.paragraph,
            required=False,
            default="No reason provided."
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction:discord.Interaction):
        await self.view.blacklist_user(reason=f"{self.reason}", interaction=interaction)

async def setup(bot):
    await bot.add_cog(bug_report(bot))