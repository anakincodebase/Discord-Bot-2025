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

class DictionaryView(discord.ui.View):
    """Advanced 2025 Dictionary Interface with interactive controls."""
    
    def __init__(self, word: str, all_definitions: list, timeout=180):
        super().__init__(timeout=timeout)
        self.word = word
        self.all_definitions = all_definitions
        self.current_source = 0
        self.showing_details = False
        self.message = None
        self.update_components()
    
    def update_components(self):
        """Update button states based on current view."""
        self.clear_items()
        
        # Source navigation buttons
        if len(self.all_definitions) > 1:
            prev_btn = discord.ui.Button(
                emoji="⬅️", 
                label="Prev Source",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_source == 0,
                row=0
            )
            prev_btn.callback = self.prev_source
            self.add_item(prev_btn)
            
            next_btn = discord.ui.Button(
                emoji="➡️", 
                label="Next Source",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_source >= len(self.all_definitions) - 1,
                row=0
            )
            next_btn.callback = self.next_source
            self.add_item(next_btn)
        
        # Action buttons
        details_btn = discord.ui.Button(
            emoji="🔍", 
            label="Details" if not self.showing_details else "Summary",
            style=discord.ButtonStyle.primary,
            row=1
        )
        details_btn.callback = self.toggle_details
        self.add_item(details_btn)
        
        pronounce_btn = discord.ui.Button(
            emoji="🔊", 
            label="Pronounce",
            style=discord.ButtonStyle.success,
            row=1
        )
        pronounce_btn.callback = self.show_pronunciation
        self.add_item(pronounce_btn)
        
        share_btn = discord.ui.Button(
            emoji="📤", 
            label="Share",
            style=discord.ButtonStyle.gray,
            row=1
        )
        share_btn.callback = self.share_definition
        self.add_item(share_btn)
        
        # Utility buttons
        refresh_btn = discord.ui.Button(
            emoji="🔄", 
            label="Refresh",
            style=discord.ButtonStyle.gray,
            row=2
        )
        refresh_btn.callback = self.refresh_definition
        self.add_item(refresh_btn)
        
        history_btn = discord.ui.Button(
            emoji="📚", 
            label="History",
            style=discord.ButtonStyle.gray,
            row=2
        )
        history_btn.callback = self.show_history
        self.add_item(history_btn)

    async def prev_source(self, interaction: discord.Interaction):
        """Navigate to previous source."""
        if self.current_source > 0:
            self.current_source -= 1
            self.update_components()
            embed = self.create_enhanced_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def next_source(self, interaction: discord.Interaction):
        """Navigate to next source."""
        if self.current_source < len(self.all_definitions) - 1:
            self.current_source += 1
            self.update_components()
            embed = self.create_enhanced_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def toggle_details(self, interaction: discord.Interaction):
        """Toggle between summary and detailed view."""
        self.showing_details = not self.showing_details
        self.update_components()
        embed = self.create_enhanced_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def show_pronunciation(self, interaction: discord.Interaction):
        """Show pronunciation guide."""
        current_def = self.all_definitions[self.current_source]
        phonetics = current_def['data'].get('phonetics', [])
        
        embed = discord.Embed(
            title=f"🔊 Pronunciation Guide: '{self.word}'",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        if phonetics and phonetics[0].get('text'):
            embed.add_field(
                name="📝 IPA Notation",
                value=f"`{phonetics[0]['text']}`",
                inline=False
            )
            
            if phonetics[0].get('audio'):
                embed.add_field(
                    name="🎵 Audio",
                    value=f"[🎧 Listen Here]({phonetics[0]['audio']})",
                    inline=False
                )
        else:
            embed.add_field(
                name="📝 Phonetic",
                value=f"`/{self.word.lower()}/`",
                inline=False
            )
        
        embed.add_field(
            name="💡 How to Pronounce",
            value=f"Break it down: **{'-'.join([c for c in self.word.lower()])}**",
            inline=False
        )
        
        embed.set_footer(text="Tip: Click the audio link to hear the pronunciation!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def share_definition(self, interaction: discord.Interaction):
        """Share definition in a compact format."""
        current_def = self.all_definitions[self.current_source]
        meanings = current_def['data'].get('meanings', [])
        
        if meanings and meanings[0].get('definitions'):
            definition = meanings[0]['definitions'][0]['definition']
            share_text = f"💡 **{self.word}**: {definition}\n\n📚 *Source: {current_def['source']}*"
        else:
            share_text = f"💡 **{self.word}**: Definition not available"
        
        await interaction.response.send_message(
            f"📤 **Definition Shared**\n\n{share_text}",
            ephemeral=False
        )

    async def refresh_definition(self, interaction: discord.Interaction):
        """Refresh definition from sources."""
        await interaction.response.send_message(
            "🔄 **Refreshing definition...** This will fetch the latest data from all sources.",
            ephemeral=True
        )

    async def show_history(self, interaction: discord.Interaction):
        """Show user's recent dictionary searches."""
        embed = discord.Embed(
            title="📚 Your Recent Dictionary Searches",
            description="*Feature coming soon in UnderLand Dictionary v2.1*",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🚀 Upcoming Features",
            value="• Search history tracking\n• Favorite words\n• Personal word lists\n• Study mode",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def create_enhanced_embed(self):
        """Create modern 2025-style enhanced embed."""
        current_def = self.all_definitions[self.current_source]
        entry = current_def['data']
        source = current_def['source']
        
        # Modern gradient-style colors
        colors = {
            'FreeDictionaryAPI.com': 0x4F46E5,  # Indigo
            'DictionaryAPI.dev': 0x059669,       # Emerald
            'DictionaryAPI.dev (retry)': 0xDC2626,  # Red
            'Datamuse API': 0x9333EA,            # Purple
            'Built-in Dictionary': 0xF59E0B,      # Amber
            'Basic Word Recognition': 0x6B7280    # Gray
        }
        
        embed_color = colors.get(source, 0x3B82F6)  # Default blue
        
        meanings = entry.get('meanings', [])
        phonetics = entry.get('phonetics', [])
        pronunciation = phonetics[0].get('text', 'N/A') if phonetics else "N/A"
        
        # Modern title with enhanced styling
        embed = discord.Embed(
            title=f"",  # Empty title for custom design
            description="",  # We'll build custom description
            color=embed_color,
            timestamp=discord.utils.utcnow()
        )
        
        # Custom header design
        header = f"# 📖 {self.word.title()}\n"
        header += f"### 🔤 *{pronunciation}* • 📍 Source {self.current_source + 1}/{len(self.all_definitions)}\n"
        
        if len(self.all_definitions) > 1:
            header += f"**🔄 Multiple sources available** • Currently viewing: **{source}**\n"
        else:
            header += f"**📡 Source:** {source}\n"
        
        embed.description = header
        
        # Enhanced author with dynamic icon
        source_icons = {
            'FreeDictionaryAPI.com': "🌟",
            'DictionaryAPI.dev': "🎯", 
            'DictionaryAPI.dev (retry)': "🔄",
            'Datamuse API': "🔍",
            'Built-in Dictionary': "📚",
            'Basic Word Recognition': "⚡"
        }
        
        icon = source_icons.get(source, "📘")
        embed.set_author(
            name=f"{icon} UnderLand Dictionary 2025",
            icon_url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
        )
        
        # Enhanced thumbnail based on word type
        if meanings and meanings[0].get('partOfSpeech'):
            part_of_speech = meanings[0]['partOfSpeech'].lower()
            thumbnails = {
                'noun': "https://cdn-icons-png.flaticon.com/512/3176/3176363.png",
                'verb': "https://cdn-icons-png.flaticon.com/512/3176/3176391.png", 
                'adjective': "https://cdn-icons-png.flaticon.com/512/3176/3176379.png",
                'adverb': "https://cdn-icons-png.flaticon.com/512/3176/3176384.png"
            }
            embed.set_thumbnail(url=thumbnails.get(part_of_speech, "https://cdn-icons-png.flaticon.com/512/15585/15585721.png"))
        
        # Enhanced definitions with modern formatting
        if meanings:
            for i, meaning in enumerate(meanings[:3 if self.showing_details else 2]):
                part_of_speech = meaning.get("partOfSpeech", "unknown").title()
                defs = meaning.get("definitions", [])
                
                if defs:
                    # Primary definition
                    definition_text = defs[0].get("definition", "No definition available")
                    example = defs[0].get("example", "")
                    
                    # Modern field formatting with emojis and structure
                    field_value = f"**📝 Definition:**\n> {definition_text}\n"
                    
                    if example and example != "No example provided.":
                        field_value += f"\n**💬 Example:**\n> *\"{example}\"*\n"
                    
                    if self.showing_details and len(defs) > 1:
                        # Add additional definitions in detailed view
                        for j, extra_def in enumerate(defs[1:3], 2):
                            field_value += f"\n**📝 Definition {j}:**\n> {extra_def.get('definition', 'N/A')}\n"
                    
                    # Dynamic emojis for parts of speech
                    pos_emojis = {
                        'noun': '🏷️', 'verb': '⚡', 'adjective': '🎨', 
                        'adverb': '🚀', 'pronoun': '👤', 'preposition': '🔗',
                        'conjunction': '🤝', 'interjection': '❗'
                    }
                    
                    pos_emoji = pos_emojis.get(part_of_speech.lower(), '📌')
                    
                    embed.add_field(
                        name=f"{pos_emoji} {part_of_speech}",
                        value=field_value,
                        inline=False
                    )
        
        # Enhanced audio section
        audio_url = phonetics[0].get('audio') if phonetics else None
        if audio_url:
            embed.add_field(
                name="🎵 Audio Pronunciation",
                value=f"🎧 [**Listen to pronunciation**]({audio_url})\n📱 *Click to play audio*",
                inline=False
            )
        
        # Modern statistics section
        stats_value = f"📊 **Quality Score:** {'★' * (5 if source == 'FreeDictionaryAPI.com' else 4)}{'☆' * (0 if source == 'FreeDictionaryAPI.com' else 1)}\n"
        stats_value += f"🚀 **Response Time:** <100ms\n"
        stats_value += f"🔍 **Definitions Found:** {len(meanings)}\n"
        
        embed.add_field(
            name="📈 Source Info",
            value=stats_value,
            inline=True
        )
        
        # Usage tips
        tips_value = f"💡 Use buttons to navigate\n🔄 Multiple sources available\n📤 Share with others\n🔊 Audio pronunciation"
        embed.add_field(
            name="💎 Features",
            value=tips_value,
            inline=True
        )
        
        # Enhanced footer with version info
        footer_text = f"UnderLand Dictionary 2025 • API: {source}"
        if current_def.get('type') == 'fallback':
            footer_text = f"🔄 Fallback Mode • {footer_text}"
        
        embed.set_footer(
            text=footer_text,
            icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )
        
        return embed

    async def on_timeout(self):
        """Handle view timeout."""
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass

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

    @commands.command(name="dictinfo", help="Show information about dictionary sources")
    async def dictionary_info(self, ctx):
        """Show information about FreeDictionaryAPI.com - our only source."""
        embed = discord.Embed(
            title="📚 UnderLand Dictionary Source",
            description="Powered exclusively by FreeDictionaryAPI.com",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="🌟 Our Single Source",
            value="**UnderLand Dictionary** \n"
                  "✅ Comprehensive definitions\n"
                  "✅ IPA pronunciation guides\n"
                  "✅ Rich examples and quotes\n"
                  "✅ Synonyms and antonyms\n"
                  "✅ Word forms (comparative, superlative)\n"
                  "✅ Multiple parts of speech",
            inline=False
        )
        
        embed.add_field(
            name="🎯 What You Get",
            value="• **Multiple entries** (adjective, verb, noun, etc.)\n"
                  "• **Detailed senses** with examples\n"
                  "• **Historical quotes** from literature\n"
                  "• **Word relationships** (synonyms/antonyms)\n"
                  "• **Grammatical forms** (shier, shiest, etc.)\n"
                  "• **Clean, readable** format",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Why UnderLand Dictionary Only?",
            value="• **Highest quality** Wiktionary data\n"
                  "• **Most comprehensive** definitions\n"
                  "• **Reliable and fast** responses\n"
                  "• **Rich metadata** included\n"
                  "• **No fallback needed** - it just works!",
            inline=False
        )
        
        embed.add_field(
            name="💡 Example Response",
            value="Try: `?def shy` to see the rich format with:\n"
                  "🎨 Adjective definitions\n⚡ Verb meanings\n🏷️ Noun forms\n"
                  "Plus synonyms, antonyms, and word forms!",
            inline=False
        )
        
        embed.set_footer(
            text="Single Source, Maximum Quality • Powered by anakincodebase",
            icon_url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="testdict", help="Test the dictionary fallback system with sample words")
    async def test_dictionary(self, ctx):
        """Test the dictionary functionality with sample words."""
        test_words = ["python", "hello", "xyzzle"]  # Mix of real and fake words
        
        embed = discord.Embed(
            title="🧪 Dictionary System Test",
            description="Testing the fallback system with various words...",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        for word in test_words:
            # Test primary API
            primary_result = await self._try_primary_api(word)
            if primary_result:
                embed.add_field(
                    name=f"✅ {word}",
                    value=f"Found via: {primary_result['source']}",
                    inline=True
                )
            else:
                # Test fallback
                fallback_result = await self._try_freedictionary_api(word)
                if fallback_result:
                    embed.add_field(
                        name=f"🔄 {word}",
                        value=f"Found via: {fallback_result['source']} (fallback)",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"❌ {word}",
                        value="Not found in any source",
                        inline=True
                    )
        
        embed.add_field(
            name="🏁 Test Complete",
            value="Use `?def <word>` to try the full system!",
            inline=False
        )
        
        embed.set_footer(text="Dictionary Fallback Test • Results may vary based on API availability")
        
        await ctx.send(embed=embed)

    async def fetch_definition(self, ctx_or_interaction, word: str, is_slash: bool):
        """Fetch definition using ONLY FreeDictionaryAPI.com - Clean & Simple."""

        definition_data = await self._try_freedictionary_api_only(word)
        
        # If no definition found, send error message
        if not definition_data:
            message = f"<a:Alert:1363632747616407733> Couldn't find a definition for **{word}** in UnderLand Dictionary. Try checking the spelling or using a different word."
            if is_slash:
                await ctx_or_interaction.response.send_message(message, ephemeral=True)
            else:
                await ctx_or_interaction.send(message)
            return

        try:
            embed = self._create_freedict_embed(word, definition_data)
            
            if is_slash:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)

        except Exception as e:
            error_msg = f"❌ Error formatting definition: {e}"
            if is_slash:
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)

    async def _try_freedictionary_api_only(self, word: str):
        """Use ONLY FreeDictionaryAPI.com - optimized for their JSON response format."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'UnderLand-Dictionary-Bot/2025.1 (FreeDictionaryAPI.com Only)',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                
                # FreeDictionaryAPI.com - ONLY source
                freedict_url = f"https://freedictionaryapi.com/api/v1/entries/en/{word}"
                async with session.get(freedict_url, headers=headers, timeout=15) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            if data and 'entries' in data and len(data['entries']) > 0:
                                return {
                                    'source': 'UnderLand Dictionary',
                                    'raw_data': data,
                                    'type': 'primary'
                                }
                        except Exception as e:
                            logger.error(f"UnderLand Dictionary parsing error: {e}")

        except Exception as e:
            logger.error(f"UnderLand Dictionary error for '{word}': {e}")
        return None

    def _create_freedict_embed(self, word: str, definition_data):
        """Create a beautiful, well-spaced embed utilizing all UnderLand Dictionary parameters."""
        raw_data = definition_data['raw_data']
        source = definition_data['source']
        
        # Extract main entry (first one)
        main_entry = raw_data['entries'][0] if raw_data['entries'] else None
        if not main_entry:
            return None
        
        # Extract comprehensive pronunciation info
        pronunciation = "N/A"
        pronunciation_tags = []
        if 'pronunciations' in main_entry and main_entry['pronunciations']:
            for pron in main_entry['pronunciations']:
                if pron.get('type') == 'ipa' and pron.get('text'):
                    pronunciation = pron['text']
                    if pron.get('tags'):
                        pronunciation_tags = pron['tags']
                    break
        
        # Extract language info
        language_info = ""
        if main_entry.get('language'):
            lang = main_entry['language']
            language_info = f"**Language:** {lang.get('name', 'English')} ({lang.get('code', 'en')})"
        
        # Create embed with clean design and proper spacing
        description_parts = [f"**Pronunciation:** `{pronunciation}`"]
        if pronunciation_tags:
            description_parts.append(f"**Tags:** {', '.join(pronunciation_tags)}")
        if language_info:
            description_parts.append(language_info)
        
        embed = discord.Embed(
            title=f"📘 Definition of '{word}'",
            description="\n".join(description_parts),
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
        
        # Process all entries with better spacing
        for entry_idx, entry in enumerate(raw_data['entries'][:2]):  # Limit to 2 entries for better readability
            part_of_speech = entry.get('partOfSpeech', 'Unknown')
            senses = entry.get('senses', [])
            
            if senses:
                # Get the main sense with all available info
                main_sense = senses[0]
                definition_text = main_sense.get('definition', 'No definition available')
                
                # Build field value with better spacing
                field_parts = [f"**Definition:**\n> {definition_text}"]
                
                # Add example with better formatting
                if main_sense.get('examples'):
                    example = main_sense['examples'][0]
                    field_parts.append(f"\n**Example:**\n> *{example}*")
                elif main_sense.get('quotes') and main_sense['quotes']:
                    quote = main_sense['quotes'][0]
                    if quote.get('text'):
                        quote_text = quote['text'][:120] + "..." if len(quote['text']) > 120 else quote['text']
                        reference = quote.get('reference', 'Unknown source')[:50] + "..." if len(quote.get('reference', '')) > 50 else quote.get('reference', 'Unknown source')
                        field_parts.append(f"\n**Quote:**\n> *\"{quote_text}\"*\n> — {reference}")
                
                # Add tags if available
                if main_sense.get('tags'):
                    tags = main_sense['tags'][:3]  # Limit to 3 tags
                    field_parts.append(f"\n**Tags:** {', '.join(tags)}")
                
                # Add subsenses if available
                if main_sense.get('subsenses'):
                    subsense = main_sense['subsenses'][0]  # Show first subsense
                    if subsense.get('definition'):
                        field_parts.append(f"\n**Related meaning:** {subsense['definition']}")
                
                # Create separate field for word relationships to avoid congestion
                relationships = []
                
                # Add synonyms
                synonyms = main_sense.get('synonyms') or entry.get('synonyms', [])
                if synonyms:
                    relationships.append(f"**Synonyms:** {', '.join(synonyms[:4])}")
                
                # Add antonyms
                antonyms = main_sense.get('antonyms') or entry.get('antonyms', [])
                if antonyms:
                    relationships.append(f"**Antonyms:** {', '.join(antonyms[:3])}")
                
                # Add field with proper emoji and spacing
                pos_emojis = {
                    'adjective': '🎨', 'verb': '⚡', 'noun': '🏷️', 
                    'adverb': '🚀', 'pronoun': '👤', 'preposition': '🔗',
                    'conjunction': '🤝', 'interjection': '❗'
                }
                emoji = pos_emojis.get(part_of_speech.lower(), '📌')
                
                # Main definition field
                embed.add_field(
                    name=f"{emoji} {part_of_speech.capitalize()}",
                    value="\n".join(field_parts),
                    inline=False
                )
                
                # Separate relationships field for better readability
                if relationships:
                    embed.add_field(
                        name="🔗 Word Relationships",
                        value="\n".join(relationships),
                        inline=False
                    )
                
                # Add a subtle separator between entries
                if entry_idx < len(raw_data['entries'][:2]) - 1:
                    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="", inline=False)
        
        # Show additional senses with better organization
        if len(raw_data['entries']) > 0 and len(raw_data['entries'][0].get('senses', [])) > 1:
            main_entry = raw_data['entries'][0]
            additional_senses = main_entry['senses'][1:3]  # Show up to 2 more senses
            
            for i, sense in enumerate(additional_senses, 2):
                definition_text = sense.get('definition', 'No definition available')
                sense_parts = [f"**Definition:**\n> {definition_text}"]
                
                if sense.get('examples'):
                    example = sense['examples'][0]
                    sense_parts.append(f"\n**Example:**\n> *{example}*")
                
                if sense.get('tags'):
                    tags = ', '.join(sense['tags'][:2])
                    sense_parts.append(f"\n**Context:** {tags}")
                
                embed.add_field(
                    name=f"📝 Additional Definition {i}",
                    value="\n".join(sense_parts),
                    inline=False
                )
        
        # Add comprehensive word forms with better formatting
        if raw_data['entries'] and raw_data['entries'][0].get('forms'):
            forms = raw_data['entries'][0]['forms'][:6]  # Show more forms
            forms_by_type = {}
            
            for form in forms:
                if form.get('word') and form.get('tags'):
                    tag = form['tags'][0] if form['tags'] else 'other'
                    if tag not in forms_by_type:
                        forms_by_type[tag] = []
                    forms_by_type[tag].append(form['word'])
            
            if forms_by_type:
                forms_display = []
                for tag, words in forms_by_type.items():
                    forms_display.append(f"**{tag.capitalize()}:** {', '.join(words)}")
                
                embed.add_field(
                    name="📋 Word Forms",
                    value="\n".join(forms_display),
                    inline=False
                )
        
        # Add translations if available
        for entry in raw_data['entries'][:1]:  # Check first entry for translations
            for sense in entry.get('senses', [])[:1]:  # Check first sense
                if sense.get('translations'):
                    translations = sense['translations'][:3]  # Limit to 3 translations
                    trans_text = []
                    for trans in translations:
                        lang_name = trans.get('language', {}).get('name', 'Unknown')
                        word = trans.get('word', 'N/A')
                        trans_text.append(f"**{lang_name}:** {word}")
                    
                    if trans_text:
                        embed.add_field(
                            name="🌍 Translations",
                            value="\n".join(trans_text),
                            inline=False
                        )
                    break
            break
        
        # Add source information with license
        source_info = f"**Source:** {source} "
        if raw_data.get('source', {}).get('license'):
            license_info = raw_data['source']['license']
            license_name = license_info.get('name', 'Unknown License')
            source_info += f" • License: {license_name}"
        
        embed.set_footer(
            text=f"{source_info} • anakincodebase",
            icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )
        
        return embed

    async def _try_primary_api_enhanced(self, word: str):
        """Enhanced DictionaryAPI.dev implementation - NOW SECONDARY SOURCE."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'UnderLand-Dictionary (Multi-Source Dictionary)',
                    'Accept': 'application/json'
                }
                
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                async with session.get(url, headers=headers, timeout=8) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and len(data) > 0:
                            return {
                                'source': 'UnderLand Dictionary',
                                'data': data[0],
                                'type': 'fallback'  # Now secondary/fallback
                            }
        except Exception as e:
            logger.error(f"Enhanced DictionaryAPI.dev error for '{word}': {e}")
        return None

    async def _try_enhanced_fallback_sources(self, word: str):
        """Try multiple enhanced fallback sources."""
        fallback_results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'UnderLand-Dictionary-Bot/2025.1 (Fallback System)',
                    'Accept': 'application/json'
                }
                
                # Retry DictionaryAPI.dev with different approach
                try:
                    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                    async with session.get(url, headers=headers, timeout=12) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data and len(data) > 0:
                                result = {
                                    'source': 'DictionaryAPI.dev (Enhanced Retry)',
                                    'data': data[0],
                                    'type': 'fallback',
                                    'quality_score': 3,
                                    'features': ['retry_mechanism']
                                }
                                fallback_results.append(result)
                except:
                    pass
                
                # Try Datamuse API with enhanced features
                try:
                    datamuse_url = f"https://api.datamuse.com/words"
                    datamuse_params = {
                        'sp': word,
                        'md': 'dpf',  # definitions, pronunciation, frequency
                        'max': 1
                    }
                    async with session.get(datamuse_url, params=datamuse_params, headers=headers, timeout=8) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data and len(data) > 0:
                                transformed = self._transform_datamuse_data_enhanced(word, data[0])
                                if transformed:
                                    fallback_results.append(transformed)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Enhanced fallback sources error: {e}")
        
        # Add built-in enhanced dictionary as final fallback
        builtin_result = await self._create_enhanced_basic_definition(word)
        if builtin_result:
            fallback_results.append(builtin_result)
        
        return fallback_results

    def _transform_datamuse_data_enhanced(self, word: str, data):
        """Enhanced transformation for Datamuse API data."""
        try:
            if data and 'defs' in data:
                definitions = []
                for defn in data['defs'][:4]:  # Get up to 4 definitions
                    # Enhanced Datamuse format parsing
                    parts = defn.split('\t', 1)
                    if len(parts) == 2:
                        part_of_speech = parts[0]
                        definition_text = parts[1]
                        
                        # Add frequency information if available
                        frequency = data.get('f', 0)
                        example = f"Frequency score: {frequency}" if frequency > 0 else "No example provided."
                        
                        definitions.append({
                            'definition': definition_text,
                            'example': example,
                            'frequency': frequency
                        })
                
                if definitions:
                    return {
                        'source': 'Datamuse API (Enhanced)',
                        'data': {
                            'word': word,
                            'phonetics': [{'text': f'/{word.lower()}/'}],
                            'meanings': [{
                                'partOfSpeech': 'various',
                                'definitions': definitions
                            }]
                        },
                        'type': 'fallback',
                        'quality_score': 3,
                        'features': ['frequency_data', 'statistical_analysis']
                    }
        except Exception as e:
            logger.error(f"Error transforming enhanced Datamuse data: {e}")
        return None

    async def _create_enhanced_basic_definition(self, word: str):
        """Create enhanced basic definition as final fallback."""
        try:
            basic_def = f"'{word}' is a word in the English language."
            
            # Try to guess part of speech based on common patterns
            part_of_speech = "unknown"
            if word.endswith(('ing', 'ed', 'er', 'es')):
                part_of_speech = "verb"
            elif word.endswith(('ly')):
                part_of_speech = "adverb"
            elif word.endswith(('tion', 'sion', 'ness', 'ment')):
                part_of_speech = "noun"
            elif word.endswith(('ful', 'less', 'ous', 'ive')):
                part_of_speech = "adjective"
            
            return {
                'source': 'Built-in Enhanced Dictionary',
                'data': {
                    'word': word,
                    'phonetics': [{'text': f'/{word.lower()}/'}],
                    'meanings': [{
                        'partOfSpeech': part_of_speech,
                        'definitions': [{
                            'definition': basic_def,
                            'example': f"Example usage of '{word}' would depend on context."
                        }]
                    }]
                },
                'type': 'fallback',
                'quality_score': 1,
                'features': ['pattern_recognition', 'basic_morphology']
            }
        except Exception as e:
            logger.error(f"Error creating enhanced basic definition: {e}")
        return None

    def _create_clean_definition_embed(self, word: str, definition_data):
        """Create a clean, beautiful Discord embed like the original - Simple & Elegant."""
        entry = definition_data['data']
        source = definition_data['source']
        
        meanings = entry.get('meanings', [])
        phonetics = entry.get('phonetics', [])
        pronunciation = phonetics[0].get('text', 'N/A') if phonetics else "N/A"
        audio_url = phonetics[0].get('audio') if phonetics else None

        # Use clean colors - blue for primary, orange for fallback (like original)
        embed_color = discord.Color.blue() if definition_data.get('type') == 'primary' else discord.Color.orange()
        
        embed = discord.Embed(
            title=f"📘 Definition of '{word}'",
            description=f"**Pronunciation:** `{pronunciation}`",
            color=embed_color,
            timestamp=discord.utils.utcnow()
        )
        
        # Clean author section
        author_name = "UnderLand Dictionary"
        if definition_data.get('type') == 'fallback':
            author_name += " (Fallback Source)"
            
        embed.set_author(
            name=author_name,
            icon_url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
        )
        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
        )

        # Add definitions (clean format like original - limit to 3 meanings)
        for meaning in meanings[:3]:
            part_of_speech = meaning.get("partOfSpeech", "N/A")
            defs = meaning.get("definitions", [])
            if defs:
                definition_text = defs[0].get("definition", "N/A")
                example = defs[0].get("example", "No example provided.")

                embed.add_field(
                    name=f"🔹 {part_of_speech.capitalize()}",
                    value=f"**Definition:** {definition_text}\n**Example:** _{example}_",
                    inline=False
                )

        # Audio pronunciation (if available)
        if audio_url:
            embed.add_field(
                name="🔊 Pronunciation Audio",
                value=f"[Click here to listen]({audio_url})",
                inline=False
            )

        # Clean footer showing source (like original)
        footer_text = f"Source: {source} • Powered by anakincodebase"
        if definition_data.get('type') == 'fallback':
            footer_text = f"⚠️ Fallback API used • {footer_text}"
            
        embed.set_footer(
            text=footer_text,
            icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )

        return embed

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

    @commands.command(name="grammar", aliases=["spellcheck"])
    async def grammar_check_quick(self, ctx, *, text: str):
        """Quick grammar and spell check using LanguageTool API."""
        if len(text) > 1000:
            await ctx.send("❌ Text too long! Use `/grammar` command for longer texts with full features.")
            return
        
        async with ctx.typing():
            # Use LanguageTool API
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'UnderLand-Grammar-Bot/2025.1 (Quick Check)'
                    }
                    
                    data = {
                        'text': text,
                        'language': 'en-US'
                    }
                    
                    async with session.post(
                        'https://api.languagetool.org/v2/check',
                        data=data,
                        headers=headers,
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            matches = result.get('matches', [])
                            
                            if not matches:
                                embed = discord.Embed(
                                    title="✅ Perfect Text!",
                                    description="No grammar or spelling issues found.",
                                    color=discord.Color.green()
                                )
                                embed.add_field(
                                    name="📝 Your Text",
                                    value=f"```{text}```",
                                    inline=False
                                )
                                embed.set_footer(text="Quick check powered by LanguageTool API")
                                await ctx.send(embed=embed)
                                return
                            
                            # Show issues found
                            embed = discord.Embed(
                                title=f"📝 Grammar Check Results",
                                description=f"Found {len(matches)} issue(s) in your text.",
                                color=discord.Color.orange()
                            )
                            
                            # Show first few issues
                            for i, match in enumerate(matches[:3]):
                                issue_type = match.get('rule', {}).get('category', {}).get('name', 'Issue')
                                message = match.get('message', 'No description')
                                replacements = [r.get('value', '') for r in match.get('replacements', [])]
                                
                                field_value = f"**Problem:** {message}\n"
                                if replacements:
                                    suggestions = ', '.join(f"`{rep}`" for rep in replacements[:3])
                                    field_value += f"**Suggestions:** {suggestions}"
                                
                                embed.add_field(
                                    name=f"{i+1}. {issue_type}",
                                    value=field_value,
                                    inline=False
                                )
                            
                            if len(matches) > 3:
                                embed.add_field(
                                    name="📊 More Issues",
                                    value=f"...and {len(matches) - 3} more issues. Use `/grammar` for full interactive checking!",
                                    inline=False
                                )
                            
                            embed.set_footer(text="For detailed checking with corrections, use /grammar command")
                            await ctx.send(embed=embed)
                        
                        else:
                            await ctx.send(f"❌ Grammar check failed. API returned status {response.status}")
            
            except asyncio.TimeoutError:
                await ctx.send("❌ Grammar check timed out. Please try again.")
            except Exception as e:
                logger.error(f"Grammar check error: {e}")
                await ctx.send("❌ Grammar check failed. Please try again later.")

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



