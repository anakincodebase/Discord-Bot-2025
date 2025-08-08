"""
Utility commands for the Discord bot.
"""

import asyncio
import datetime
import logging
from typing import Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

# Removed llm_chat import for deployment version without AI dependencies

logger = logging.getLogger(__name__)

class WhoisView(discord.ui.View):
    """View for paginated whois command."""
    
    def __init__(self, roles_pages, timeout=60):
        super().__init__(timeout=timeout)
        self.pages = roles_pages
        self.current_page = 0
        self.message = None
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        self.add_item(discord.ui.Button(
            label="◀️", 
            style=discord.ButtonStyle.secondary, 
            custom_id="prev", 
            disabled=self.current_page == 0
        ))
        self.add_item(discord.ui.Button(
            label="▶️", 
            style=discord.ButtonStyle.secondary, 
            custom_id="next", 
            disabled=self.current_page == len(self.pages) - 1
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, custom_id="prev", row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, custom_id="next", row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

class HelpView(discord.ui.View):
    """View for paginated help command."""
    
    def __init__(self, ctx, embeds):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.embeds = embeds
        self.index = 0
        self.message = None

    async def send_initial_message(self):
        self.message = await self.ctx.send(embed=self.embeds[self.index], view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="⏮️ First", style=discord.ButtonStyle.secondary)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = 0
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="◀️ Prev", style=discord.ButtonStyle.primary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await interaction.response.edit_message(embed=self.embeds[self.index], view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.embeds) - 1:
            self.index += 1
            await interaction.response.edit_message(embed=self.embeds[self.index], view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="⏭️ Last", style=discord.ButtonStyle.secondary)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = len(self.embeds) - 1
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

class Dictionary(commands.Cog):
    """Dictionary lookup functionality."""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="def", help="Get the definition of a word.")
    async def define_word_prefix(self, ctx, *, word: str):
        await self.fetch_definition(ctx, word, is_slash=False)

    @app_commands.command(name="def", description="Define an English word")
    @app_commands.describe(word="The word you want to define")
    async def define_word_slash(self, interaction: discord.Interaction, word: str):
        await self.fetch_definition(interaction, word, is_slash=True)

    async def fetch_definition(self, ctx_or_interaction, word: str, is_slash: bool):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            # Try primary API first - api.dictionaryapi.dev
            try:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = self._create_embed_from_primary_api(word, data)
                        if embed:
                            if is_slash:
                                await ctx_or_interaction.response.send_message(embed=embed)
                            else:
                                await ctx_or_interaction.send(embed=embed)
                            return
            except Exception as e:
                logger.error(f"Primary API (dictionaryapi.dev) error: {e}")

            # FreeDictionaryAPI.com - now fallback source
            try:
                freedict_url = f"https://freedictionaryapi.com/api/v1/entries/en/{word}"
                async with session.get(freedict_url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and 'entries' in data and len(data['entries']) > 0:
                            embed = self._transform_real_freedictionary_data_enhanced(word, data)
                            if embed:
                                if is_slash:
                                    await ctx_or_interaction.response.send_message(embed=embed)
                                else:
                                    await ctx_or_interaction.send(embed=embed)
                                return
            except Exception as e:
                logger.error(f"FreeDictionaryAPI.com parsing error: {e}")

        # If all APIs fail
        message = f"<a:Alert:1363632747616407733> Couldn't find a definition for **{word}**."
        if is_slash:
            await ctx_or_interaction.response.send_message(message, ephemeral=True)
        else:
            await ctx_or_interaction.send(message)

    def _create_embed_from_primary_api(self, word: str, data):
        """Create embed from primary API (dictionaryapi.dev) response."""
        try:
            entry = data[0]
            meanings = entry['meanings']
            phonetics = entry.get("phonetics", [])
            pronunciation = phonetics[0].get("text") if phonetics else "N/A"
            audio_url = phonetics[0].get("audio") if phonetics else None

            embed = discord.Embed(
                title=f"📘 Definition of '{word}'",
                description=f"**Pronunciation:** `{pronunciation}`",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_author(
                name="UnderLand Dictionary",
                icon_url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
            )
            embed.set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
            )

            for meaning in meanings[:3]:
                part_of_speech = meaning.get("partOfSpeech", "N/A")
                defs = meaning.get("definitions", [])
                definition_text = defs[0].get("definition", "N/A")
                example = defs[0].get("example", "No example provided.")

                embed.add_field(
                    name=f"🔹 {part_of_speech.capitalize()}",
                    value=f"**Definition:** {definition_text}\\n**Example:** _{example}_",
                    inline=False
                )

            if audio_url:
                embed.add_field(
                    name="🔊 Pronunciation Audio",
                    value=f"[Click here to listen]({audio_url})",
                    inline=False
                )

            embed.set_footer(
                text="Powered by anakincodebase • Source: DictionaryAPI.dev",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )

            return embed
        except Exception as e:
            logger.error(f"Error creating embed from primary API: {e}")
            return None

    def _transform_real_freedictionary_data_enhanced(self, word: str, data):
        """Transform FreeDictionaryAPI.com response to Discord embed."""
        try:
            if not data or 'entries' not in data or len(data['entries']) == 0:
                return None

            entry = data['entries'][0]
            
            # Extract phonetics/pronunciation
            pronunciation = "N/A"
            audio_url = None
            if 'phonetics' in entry and len(entry['phonetics']) > 0:
                phonetic = entry['phonetics'][0]
                pronunciation = phonetic.get('text', 'N/A')
                audio_url = phonetic.get('audio')

            embed = discord.Embed(
                title=f"📘 Definition of '{word}'",
                description=f"**Pronunciation:** `{pronunciation}`",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_author(
                name="UnderLand Dictionary",
                icon_url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
            )
            embed.set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
            )

            # Extract meanings
            if 'meanings' in entry:
                meanings = entry['meanings'][:3]  # Limit to 3 meanings
                for meaning in meanings:
                    part_of_speech = meaning.get("partOfSpeech", "N/A")
                    definitions = meaning.get("definitions", [])
                    
                    if definitions:
                        definition_text = definitions[0].get("definition", "N/A")
                        example = definitions[0].get("example", "No example provided.")

                        embed.add_field(
                            name=f"🔹 {part_of_speech.capitalize()}",
                            value=f"**Definition:** {definition_text}\\n**Example:** _{example}_",
                            inline=False
                        )

            if audio_url:
                embed.add_field(
                    name="🔊 Pronunciation Audio",
                    value=f"[Click here to listen]({audio_url})",
                    inline=False
                )

            embed.set_footer(
                text="Powered by anakincodebase",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )

            return embed
        except Exception as e:
            logger.error(f"Error transforming: {e}")
            return None

class UtilsCog(commands.Cog):
    """Utility commands cog."""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="whois")
    async def whois(self, ctx, member: Optional[discord.Member] = None):
        """Get information about a user."""
        if member is None:
            member = ctx.author

        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        role_chunks = [roles[i:i + 10] for i in range(0, len(roles), 10)] or [["None"]]

        def create_embed(role_list, index):
            embed = discord.Embed(
                title=f"🔍 Who is {member.name}?",
                description=f"Information about {member.mention}",
                color=discord.Color.blurple(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text=f"Page {index + 1}/{len(role_chunks)}")

            embed.add_field(name="🧾 Username", value=f"{member}", inline=True)
            embed.add_field(name="🆔 User ID", value=member.id, inline=True)
            embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "N/A", inline=False)
            embed.add_field(name="🎭 Bot?", value="Yes 🤖" if member.bot else "No", inline=True)
            embed.add_field(name="🛡️ System User?", value="Yes" if member.system else "No", inline=True)
            embed.add_field(name="📛 Roles", value="\\n".join(role_list), inline=False)

            if member.activity:
                embed.add_field(name="🎮 Activity", value=str(member.activity.name), inline=False)

            if member.status:
                embed.add_field(name="📶 Status", value=str(member.status).capitalize(), inline=True)

            return embed

        embeds = [create_embed(chunk, i) for i, chunk in enumerate(role_chunks)]
        view = WhoisView(embeds)
        await ctx.send(embed=embeds[0], view=view)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: Optional[discord.Member] = None):
        """Get a user's avatar."""
        if member is None:
            member = ctx.author

        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=discord.Color.blurple()
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    # Disabled for deployment version - requires AI dependencies
    # @commands.command(name="ask")
    # async def ask(self, ctx, *, message: str):
    #     """Chat with the AI assistant."""
    #     async with ctx.typing():
    #         try:
    #             response = generate_response(
    #                 message, 
    #                 str(ctx.channel.id), 
    #                 str(ctx.author.id), 
    #                 ctx.author.name
    #             )
    #             await ctx.send(response)
    #         except Exception as e:
    #             logger.error(f"Error in AI chat: {e}")
    #             await ctx.send("Sorry, I'm having trouble thinking right now. Try again later!")

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        """Make the bot repeat a message."""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="oldhelp")
    async def old_help_command(self, ctx):
        """Show basic help information (legacy version)."""
        
        embed = discord.Embed(
            title="� UnderLand Bot - Quick Help",
            description="**Basic help - Use `?help` for the enhanced help system!**",
            color=discord.Color.dark_blue()
        )
        
        embed.add_field(
            name="🎵 Music Commands",
            value="`?play <song>` • `?skip` • `?queue` • `?menu`",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Fun Commands",
            value="`?hangman` • `?trivia` • `?ship @user1 @user2`",
            inline=False
        )
        
        embed.add_field(
            name="� Social Commands",
            value="`?hug @user` • `?kiss @user` • `?bonk @user`",
            inline=False
        )
        
        embed.add_field(
            name="📚 Utility Commands",
            value="`?def <word>` • `?ask <question>` • `?whois @user`",
            inline=False
        )
        
        embed.add_field(
            name="� Enhanced Help",
            value="Use `?help` for the complete interactive help system with detailed information!",
            inline=False
        )
        
        embed.set_footer(text="Use ?help for comprehensive documentation • By anakincodebase")
        
        await ctx.send(embed=embed)

    @commands.command(name="commands", aliases=["cmds"])
    async def commands_list(self, ctx):
        """Show a quick list of all available commands."""
        
        # Collect all commands from the bot
        music_cmds = ["play", "playurl", "join", "leave", "skip", "pause", "resume", "stop", "queue", "clearqueue", "menu"]
        fun_cmds = ["hangman", "tictactoe", "trivia", "ship", "say", "replysay"]
        social_cmds = ["bonk", "kiss", "hug", "slap", "yeet", "facepalm", "rip", "kidnap", "kill", "punch", "love", "dance", "avatar"]
        util_cmds = ["def", "ask", "whois", "poll", "help", "commands"]
        mod_cmds = ["mute", "unmute", "ban", "kick", "purge", "dm"]
        
        embed = discord.Embed(
            title="📋 Quick Commands Reference",
            description="All available bot commands at a glance",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎵 Music",
            value=", ".join([f"`{cmd}`" for cmd in music_cmds]),
            inline=False
        )
        
        embed.add_field(
            name="🎮 Fun & Games", 
            value=", ".join([f"`{cmd}`" for cmd in fun_cmds]),
            inline=False
        )
        
        embed.add_field(
            name="😄 Social",
            value=", ".join([f"`{cmd}`" for cmd in social_cmds]),
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Utility",
            value=", ".join([f"`{cmd}`" for cmd in util_cmds]),
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Moderation",
            value=", ".join([f"`{cmd}`" for cmd in mod_cmds]),
            inline=False
        )
        
        embed.add_field(
            name="📱 Slash Commands",
            value="`/pomodoro`, `/def`, `/play`, `/skip`, `/queue`",
            inline=False
        )
        
        total_commands = len(music_cmds + fun_cmds + social_cmds + util_cmds + mod_cmds)
        embed.set_footer(text=f"Total: {total_commands}+ commands • Use ?help for detailed descriptions")
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome new members."""
        channel = self.bot.get_channel(self.bot.config.WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(f"🎉 Welcome {member.mention} to the server!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Say goodbye to leaving members."""
        channel = self.bot.get_channel(self.bot.config.WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(f"😢 {member.name} has left the server.")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(UtilsCog(bot))
    await bot.add_cog(Dictionary(bot))
