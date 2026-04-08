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
                view = board_view(message, board_emoji)
                await view.update_container(rxn_ct)
                board_message = await board_chnl.send(view=view)
                #rxn_emoji = await self.bot.fet
                await board_message.add_reaction(board_emoji)
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
        await interaction.response.send_modal(setup_modal(interaction))
    
    @starboard_setup.error
    async def setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command! (Required permissions: manage channels)", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return
        
        message = reaction.message
        author = message.author
        reactions = message.reactions
        server_id = message.guild.id
        server_board = loadjson(f"server_data/starboard/{server_id}")
        emoji = ""
        
        if reaction.is_custom_emoji():
            emoji = f"<:{reaction.emoji.name}:{reaction.emoji.id}>"
        
        else:
            emoji = Emoji.demojize(reaction.emoji)
        
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
            view = board_view.from_message(board_message=message, original_message=og_msg, emoji=board_emoji)
            og_reacters = await self.get_reacters(og_msg.reactions, board_emoji)
            combined_reacters = await self.combine_rxn_lists(og_reacters, reacters, og_msg.author)
            rxn_ct = len(combined_reacters)
            await view.update_container(rxn_ct, message)
            return
        
        if rxn_ct >= rxn_threshold:
            await self.update_board(server_id, message, rxn_ct, config)
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return
        
        message = reaction.message
        author = message.author
        reactions = message.reactions
        server_id = message.guild.id
        server_board = loadjson(f"server_data/starboard/{server_id}")
        emoji = ""
        
        if reaction.is_custom_emoji():
            emoji = f"<:{reaction.emoji.name}:{reaction.emoji.id}>"
        
        else:
            emoji = Emoji.demojize(reaction.emoji)
        
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
            
            if rxn_ct <= 0:
                return await message.delete()
            
            return await view.update_container(rxn_ct, message)
        
        await self.update_board(server_id=server_id, message=message, rxn_ct=rxn_ct, config=config)

class board_view(LayoutView):
    def __init__(self, message: discord.Message, emoji: str):
        super().__init__()
        self.message = message
        self.attachments = [attachment.url for attachment in message.attachments]
        self.timestamp = get_discord_timestamp(self.message.created_at.isoformat(), 'f')
        self.emoji = emoji
        self.embed_content = ""
        self.message_content = ""

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
            
        self.message_content += f"\n{self.embed_content}"
    
    async def update_container(self, rxn_ct:int, board_msg: discord.Message = None):
        self.clear_items()
        
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
    def __init__(self):
        super().__init__(channel_types=[discord.ChannelType.text], required=True)
    
    async def callback(self, interaction: discord.Interaction):
        selected_chnl = self.values[0]
        await interaction.response.send_message(selected_chnl)

class setup_modal(Modal, title="Starboard Setup"):
    def __init__(self, original_interaction: discord.Interaction):
        super().__init__()
        self.original_interaction = original_interaction
        
        self.rxn_emoji = TextInput(
            label="What emoji should be used?",
            default=":star:",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.rxn_emoji)
        
        self.note = TextDisplay(
            "-# If your emoji is a default emoji, just enter the emoji's name surrounded by ':'.\n-# If your emoji is custom, it should be formatted like this: '<:[name]:[emoji id]>'. You can find the emoji's id by typing '\\\\' in the message box then entering the emoji."
        )
        self.add_item(self.note)
        
        self.rxn_threshold = TextInput(
            label="How many reactions should be required?",
            default="4",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.rxn_threshold)
        
        self.board_chnl = Label(text="What channel should messages be sent to?", component=chnl_dropdown())
        self.add_item(self.board_chnl)
    
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
    for guild in bot.guilds:
        server_id = guild.id
        server_board = loadjson(f"server_data/starboard/{server_id}")
        config = server_board.get(0)
        server_board = {}
        server_board.update({0: config})
        savejson(f"server_data/starboard/{server_id}", server_board)
    
    await bot.add_cog(starboard(bot))