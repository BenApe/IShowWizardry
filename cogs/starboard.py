import discord
import emoji as Emoji

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from discord.ui import ActionRow, Button, Container, Separator, LayoutView, TextDisplay, Modal, TextInput, Label, ChannelSelect, Section, MediaGallery
from botutils import savejson, loadjson, get_discord_timestamp

class starboard(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    async def update_board(self, server_id, message: discord.Message, rxn_ct, config):
        message_id = message.id
        server_board = loadjson(file_name=f"server_data/starboard/{server_id}")
        msg_data = server_board.get(message_id) or {"rxn_ct": rxn_ct, "board_msg": -1, "chnl": message.channel.id}
        board_msg_id = msg_data.get("board_msg")
        server_board.update({message_id: {"rxn_ct": rxn_ct, "board_msg": board_msg_id, "chnl": message.channel.id}})
        board_emoji = config.get("emoji")
        board_chnl_id = config.get("chnl")
        board_threshold = config.get("threshold")
        board_chnl = await self.bot.fetch_channel(board_chnl_id)
        try:
            board_msg = await board_chnl.fetch_message(board_msg_id)
        except:
            board_msg = -1
        
        if rxn_ct < board_threshold:
            server_board.pop(message_id)
            try:
                await board_msg.delete()
            except:
                return
        
        elif rxn_ct >= board_threshold:
            if board_msg == -1:
                view = board_view(message, board_emoji, self.bot)
                await view.update_container(rxn_ct)
                board_message = await board_chnl.send(view=view)
                #rxn_emoji = await self.bot.fet
                
                try:
                    emoji = Emoji.emojize(board_emoji)
                except:
                    emoji = board_emoji
                
                await board_message.add_reaction(emoji)
                server_board.update({message_id: {"rxn_ct": rxn_ct, "board_msg": board_message.id, "chnl": message.channel.id}})
            else:
                view = board_view.from_message(board_message=board_msg, original_message=message, emoji=board_emoji)
                await view.update_container(rxn_ct, board_msg)
        
        savejson(f"server_data/starboard/{server_id}", server_board)
    
    async def get_reacters(self, reactions: list[discord.Reaction], find: str):
        user_ls = None
        
        for reaction in reactions:
            emoji = ""
            
            if reaction.is_custom_emoji():
                emoji = f":{reaction.emoji.name}:"
            
            else:
                emoji = Emoji.demojize(reaction.emoji)
            
            if emoji in find:
                user_ls = [user async for user in reaction.users()]
                break
        
        return user_ls
    
    async def combine_rxn_lists(self, list1: list[discord.User], list2: list[discord.User], author: discord.User):
        if author in list1:
            list1.remove(author)
        
        for user in list2:
            if user == author or user.bot or user in list1:
                continue
            
            list1.append(user)
        
        return list1
    
    async def find_original(self, message_id: int, server_board: dict):
        og_msg = None
        og_chnl = None
        
        for key, value in server_board.items():
            board_msg = value.get("board_msg")
            if board_msg == message_id:
                og_msg = key
                og_chnl = value.get("chnl")
                break
        
        try:
            channel = await self.bot.fetch_channel(og_chnl)
            message = await channel.fetch_message(og_msg)
            return message
        except Exception as e:
            print(f"Error accesing message {og_msg} in channel {og_chnl}: {e}")
        
        return None
    
    @app_commands.command(name="starboard_setup", description="(MOD) Setup the starboard for this server.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def starboard_setup(self, interaction:discord.Interaction):
        server_id = interaction.guild.id
        config = loadjson(f"server_data/starboard/{server_id}").get(0) or {"emoji": ":star:", "chnl": None, "threshold": 4}
        channel = interaction.guild.get_channel(config.get("chnl"))
        
        await interaction.response.send_modal(setup_modal(interaction, config, channel))
    
    @commands.hybrid_command(name="starboard_info", description="View the starboard config in this server.")
    async def starboard_info(self, ctx: commands.Context):
        server_id = ctx.guild.id
        info = ""
        try:
            config = loadjson(f"server_data/starboard/{server_id}").get(0)
            emoji = config.get("emoji")
            channel_id = config.get("chnl")
            threshold = config.get("threshold")
            info = f"**Emoji:** {emoji}\n**Channel:** <#{channel_id}>\n**Threshold:** {threshold}"
        except:
            info = "The starboard in this server isn't set up yet! Use </starboard_setup:1491256776320880730> to set up the starboard."
        
        embed = discord.Embed(
            title=f"Starboard for {ctx.guild.name}",
            description=info,
            color=0xF1C40F
        )
        
        await ctx.send(embed=embed)
    
    @starboard_setup.error
    async def setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command! (Required permissions: manage channels)", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        user = reaction.member
        if user.bot:
            return
        
        message_id = reaction.message_id
        channel_id = reaction.channel_id
        server_id = reaction.guild_id
        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        author = message.author
        reactions = message.reactions
        server_board = loadjson(f"server_data/starboard/{server_id}")
        emoji = ""
        
        if reaction.emoji.is_custom_emoji():
            emoji = f"<:{reaction.emoji.name}:{reaction.emoji.id}>"
        
        else:
            emoji = Emoji.demojize(reaction.emoji.name)
        
        try:
            config = server_board.get(0)
            board_emoji = config.get("emoji")
            board_chnl_id = config.get("chnl")
            rxn_threshold = config.get("threshold")
        except Exception as e:
            print(f"Error accessing starboard config: {e}")
            return

        if emoji != board_emoji:
            return
        
        reacters = await self.get_reacters(reactions, board_emoji)
        if reacters == None:
            rxn_ct = 0
        else:
            rxn_ct = len(reacters)
            
            if author in reacters:
                rxn_ct -= 1
        
        if author.bot and message.channel.id == board_chnl_id and author == self.bot.user:
            og_msg = await self.find_original(message.id, server_board)
            view = board_view.from_message(board_message=message, original_message=og_msg, emoji=board_emoji, bot=self.bot)
            og_reacters = await self.get_reacters(og_msg.reactions, board_emoji)
            combined_reacters = await self.combine_rxn_lists(og_reacters, reacters, og_msg.author)
            rxn_ct = len(combined_reacters)
            await view.update_container(rxn_ct, message)
            return
        
        if rxn_ct >= rxn_threshold:
            await self.update_board(server_id, message, rxn_ct, config)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent):
        user_id = reaction.user_id
        user = await self.bot.fetch_user(user_id)
        if user.bot:
            return
        
        message_id = reaction.message_id
        channel_id = reaction.channel_id
        server_id = reaction.guild_id
        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        author = message.author
        reactions = message.reactions
        server_board = loadjson(f"server_data/starboard/{server_id}")
        emoji = ""
        
        if reaction.emoji.is_custom_emoji():
            emoji = f"<:{reaction.emoji.name}:{reaction.emoji.id}>"
        
        else:
            emoji = Emoji.demojize(reaction.emoji.name)
        
        try:
            config = server_board.get(0)
            board_emoji = config.get("emoji")
            board_chnl_id = config.get("chnl")
        except Exception as e:
            print(f"Error accessing starboard config: {e}")
            return

        if emoji != board_emoji:
            return
        
        reacters = await self.get_reacters(reactions, board_emoji)
        if reacters == None:
            rxn_ct = 0
        else:
            rxn_ct = len(reacters)
            
            if author in reacters:
                rxn_ct -= 1
        
        if author.bot and message.channel.id == board_chnl_id and author == self.bot.user:
            og_msg = await self.find_original(message.id, server_board)
            view = board_view.from_message(board_message=message, original_message=og_msg, emoji=board_emoji)
            og_reacters = await self.get_reacters(og_msg.reactions, board_emoji)
            combined_reacters = await self.combine_rxn_lists(og_reacters, reacters, og_msg.author)
            rxn_ct = len(combined_reacters)
            await view.update_container(rxn_ct, message)
            return

        await self.update_board(server_id=server_id, message=message, rxn_ct=rxn_ct, config=config)
    
class board_view(LayoutView):
    def __init__(self, message: discord.Message, emoji: str, bot: commands.Bot):
        super().__init__()
        self.message = message
        self.attachments = [attachment.url for attachment in message.attachments]
        self.timestamp = get_discord_timestamp(self.message.created_at.isoformat(), 'f')
        self.emoji = emoji
        self.bot = bot
        self.embed_content = ""
        self.message_content = ""
        self.ref_content = ""

        if ".gif" in self.message.content:
            for word in self.message.content.split():
                if ".gif" in word:
                    self.attachments.append(word)
        
        if message.embeds:
            for embed in message.embeds:
                self.embed_content += f"### {embed.title}\n" if embed.title else " "
                self.embed_content += f"{embed.description}\n" if embed.description else " "
                
                if embed.image:
                    self.attachments.append(embed.image.url)
                
                if embed.fields:
                    for field in embed.fields:
                        name = f"**{field.name}**"
                        value = f"{field.value}"
                        self.embed_content += f"{name}\n{value}\n"
        
        if message.clean_content:
            self.message_content += message.clean_content
            
        if message.reference:
            type = message.reference.type
            ref_msg = message.reference.cached_message
            
            if ref_msg:
                if type == discord.MessageReferenceType.default:
                    self.ref_content = f"-# Reply to {ref_msg.author.mention}\n"
                    
                elif type == discord.MessageReferenceType.forward:
                    self.ref_content = f"-# Forwarded from {ref_msg.author.mention}\n"
                
                if ref_msg.clean_content:
                    self.ref_content += ref_msg.clean_content
                
                if ref_msg.embeds:
                    for embed in ref_msg.embeds:
                        self.ref_content += f"### {embed.title}\n" if embed.title else " "
                        self.ref_content += f"{embed.description}\n" if embed.description else " "
                        
                        if embed.image:
                            self.attachments.append(embed.image.url)
                        
                        if embed.fields:
                            for field in embed.fields:
                                name = f"**{field.name}**"
                                value = f"{field.value}"
                                self.ref_content += f"{name}\n{value}\n"
            
            else:
                self.ref_content = "Reference message missing from cache or could not be accessed."
        
        self.message_content += f"\n{self.embed_content}\n{self.ref_content}"
            
    
    async def update_container(self, rxn_ct:int, board_msg: discord.Message = None):
        self.clear_items()
        
        if self.message_content == None:
            return
        
        if self.attachments and (self.message.clean_content or self.embed_content):
            container = Container(
                Section(
                    f"**{self.emoji} {rxn_ct} | {self.message.author.display_name}**",
                    accessory=Button(style=discord.ButtonStyle.link, label="Original", url=self.message.jump_url)
                ),
                TextDisplay(
                    self.message_content
                ),
                attachment_view(self.attachments),
                Separator(),
                TextDisplay(
                    f"-# {self.timestamp}"
                ),
                accent_color=discord.Color.gold()
            )
            self.add_item(container)
        
        elif self.attachments:
            container = Container(
                Section(
                    f"**{self.emoji} {rxn_ct} | {self.message.author.display_name}**",
                    accessory=Button(style=discord.ButtonStyle.link, label="Original", url=self.message.jump_url)
                ),
                attachment_view(self.attachments),
                Separator(),
                TextDisplay(
                    f"-# {self.timestamp}"
                ),
                accent_color=discord.Color.gold()
            )
            self.add_item(container)
        
        else:
            container = Container(
                Section(
                    f"**{self.emoji} {rxn_ct} | {self.message.author.display_name}**",
                    accessory=Button(style=discord.ButtonStyle.link, label="Original", url=self.message.jump_url)
                ),
                TextDisplay(
                    self.message_content
                ),
                Separator(),
                TextDisplay(
                    f"-# {self.timestamp}"
                ),
                accent_color=discord.Color.gold()
            )
            self.add_item(container)
        
        if board_msg:
            await board_msg.edit(view=self)
    
    @classmethod
    def from_message(cls, board_message: discord.Message, original_message: discord.Message, emoji: str):
        view = super().from_message(board_message)
        view.clear_items()
        new_view = cls(message=original_message, emoji=emoji)
        return new_view

class attachment_view(MediaGallery):
    def __init__(self, attachments: list):
        super().__init__(*[discord.MediaGalleryItem(attachment) for attachment in attachments])

class chnl_dropdown(ChannelSelect):
    def __init__(self, channel = None):
        if channel == None:
            super().__init__(channel_types=[discord.ChannelType.text], required=True, placeholder="Choose a channel...", min_values=1, max_values=1)
        else:
            super().__init__(channel_types=[discord.ChannelType.text], required=True, default_values=[channel], placeholder="Choose a channel...", min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        selected_chnl = self.values[0]
        await interaction.response.send_message(selected_chnl)

class setup_modal(Modal, title="Starboard Setup"):
    def __init__(self, original_interaction: discord.Interaction, config: dict, channel):
        super().__init__()
        self.original_interaction = original_interaction
        self.server_id = self.original_interaction.guild.id
        self.config = config
        emoji = self.config.get("emoji")
        threshold = self.config.get("threshold")
        
        self.rxn_emoji = TextInput(
            label="What emoji should be used?",
            default=emoji,
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.rxn_emoji)
        
        self.note1 = TextDisplay(
            "-# If your emoji is a default emoji, just enter the emoji's name surrounded by ':'. Some default emojis may have multiple names in discord, you find the official names [here](https://www.webfx.com/tools/emoji-cheat-sheet/).\n\n-# If your emoji is custom, it should be formatted like this: \n-# **<:[name]:[emoji id]>**\n-# You can find the emoji's id by typing '\\\\' in the message box then entering the emoji."
        )
        self.add_item(self.note1)
        
        self.rxn_threshold = TextInput(
            label="How many reactions should be required?",
            default=threshold,
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.rxn_threshold)
        
        self.board_chnl = Label(text="What channel should messages be sent to?", component=chnl_dropdown(channel))
        self.add_item(self.board_chnl)
        
        self.note2 = TextDisplay(
            "-# The bot needs to have access to channels for them to appear in this list."
        )
        self.add_item(self.note2)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rxn_emoji = str(self.rxn_emoji)
            rxn_threshold = int(str(self.rxn_threshold))
            board_chnl = self.board_chnl.component.values[0]
            chnl_id = board_chnl.id
            server_id = self.original_interaction.guild.id
            
            server_board = loadjson(f"server_data/starboard/{server_id}")
            server_board.update({0: {"emoji": rxn_emoji, "chnl": chnl_id, "threshold": rxn_threshold}})
            savejson(f"server_data/starboard/{server_id}", server_board)
            
            await interaction.response.send_message(f"emoji: {rxn_emoji}, threshold: {rxn_threshold}, channel: {board_chnl} ({chnl_id})", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"Error saving config: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(starboard(bot))