"""
Grammar and spell checking cog using LanguageTool API.
"""

import asyncio
import logging
from typing import Optional
import re

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

class GrammarView(discord.ui.View):
    """Interactive view for grammar checking results."""
    
    def __init__(self, original_text: str, corrections: list, timeout=120):
        super().__init__(timeout=timeout)
        self.original_text = original_text
        self.corrections = corrections
        self.current_page = 0
        self.message = None
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page."""
        self.clear_items()
        
        if len(self.corrections) > 1:
            # Navigation buttons
            prev_btn = discord.ui.Button(
                emoji="⬅️",
                label="Previous",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0,
                row=0
            )
            prev_btn.callback = self.prev_correction
            self.add_item(prev_btn)
            
            next_btn = discord.ui.Button(
                emoji="➡️", 
                label="Next",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= len(self.corrections) - 1,
                row=0
            )
            next_btn.callback = self.next_correction
            self.add_item(next_btn)
        
        # Action buttons
        apply_btn = discord.ui.Button(
            emoji="✅",
            label="Apply This Fix",
            style=discord.ButtonStyle.success,
            row=1
        )
        apply_btn.callback = self.apply_correction
        self.add_item(apply_btn)
        
        apply_all_btn = discord.ui.Button(
            emoji="🔄",
            label="Apply All Fixes",
            style=discord.ButtonStyle.primary,
            row=1
        )
        apply_all_btn.callback = self.apply_all_corrections
        self.add_item(apply_all_btn)
        
        ignore_btn = discord.ui.Button(
            emoji="❌",
            label="Ignore",
            style=discord.ButtonStyle.gray,
            row=1
        )
        ignore_btn.callback = self.ignore_correction
        self.add_item(ignore_btn)
    
    async def prev_correction(self, interaction: discord.Interaction):
        """Go to previous correction."""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_correction_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def next_correction(self, interaction: discord.Interaction):
        """Go to next correction."""
        if self.current_page < len(self.corrections) - 1:
            self.current_page += 1
            self.update_buttons()
            embed = self.create_correction_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def apply_correction(self, interaction: discord.Interaction):
        """Apply the current correction."""
        correction = self.corrections[self.current_page]
        
        # Create corrected text with just this fix
        corrected_text = self.apply_single_correction(self.original_text, correction)
        
        embed = discord.Embed(
            title="✅ Correction Applied",
            description=f"Applied fix for: **{correction['issue_type']}**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Corrected Text",
            value=f"```{corrected_text}```",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def apply_all_corrections(self, interaction: discord.Interaction):
        """Apply all corrections."""
        corrected_text = self.original_text
        
        # Sort corrections by offset in reverse order to maintain positions
        sorted_corrections = sorted(self.corrections, key=lambda x: x['offset'], reverse=True)
        
        for correction in sorted_corrections:
            corrected_text = self.apply_single_correction(corrected_text, correction)
        
        embed = discord.Embed(
            title="🔄 All Corrections Applied",
            description=f"Applied {len(self.corrections)} fixes to your text.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Original Text",
            value=f"```{self.original_text[:500]}{'...' if len(self.original_text) > 500 else ''}```",
            inline=False
        )
        
        embed.add_field(
            name="✨ Corrected Text",
            value=f"```{corrected_text[:500]}{'...' if len(corrected_text) > 500 else ''}```",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def ignore_correction(self, interaction: discord.Interaction):
        """Ignore the current correction."""
        embed = discord.Embed(
            title="❌ Correction Ignored",
            description="The current suggestion has been ignored.",
            color=discord.Color.orange()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def apply_single_correction(self, text: str, correction: dict) -> str:
        """Apply a single correction to text."""
        offset = correction['offset']
        length = correction['length']
        replacement = correction['replacements'][0] if correction['replacements'] else ""
        
        return text[:offset] + replacement + text[offset + length:]
    
    def create_correction_embed(self) -> discord.Embed:
        """Create embed for current correction."""
        if not self.corrections:
            return discord.Embed(
                title="✅ No Issues Found",
                description="Your text looks great!",
                color=discord.Color.green()
            )
        
        correction = self.corrections[self.current_page]
        
        embed = discord.Embed(
            title=f"📝 Grammar Check ({self.current_page + 1}/{len(self.corrections)})",
            description=f"**Issue Type:** {correction['issue_type']}",
            color=discord.Color.orange()
        )
        
        # Show the problematic text with context
        context_start = max(0, correction['offset'] - 50)
        context_end = min(len(self.original_text), correction['offset'] + correction['length'] + 50)
        context = self.original_text[context_start:context_end]
        
        # Highlight the error
        error_start = correction['offset'] - context_start
        error_end = error_start + correction['length']
        
        highlighted = (
            context[:error_start] + 
            f"**__{context[error_start:error_end]}__**" + 
            context[error_end:]
        )
        
        embed.add_field(
            name="🔍 Context",
            value=f"...{highlighted}...",
            inline=False
        )
        
        embed.add_field(
            name="❗ Issue",
            value=correction['message'],
            inline=False
        )
        
        if correction['replacements']:
            suggestions = ', '.join(f"`{rep}`" for rep in correction['replacements'][:3])
            embed.add_field(
                name="💡 Suggestions",
                value=suggestions,
                inline=False
            )
        
        if correction.get('rule_category'):
            embed.add_field(
                name="📚 Category",
                value=correction['rule_category'],
                inline=True
            )
        
        embed.set_footer(text="Use the buttons below to apply fixes or navigate between issues")
        
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

class GrammarCheckerCog(commands.Cog):
    """Grammar and spell checking using LanguageTool API."""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.languagetool.org/v2/check"
        
        # Language options
        self.languages = {
            'en-US': 'English (US)',
            'en-GB': 'English (UK)', 
            'en-CA': 'English (Canada)',
            'en-AU': 'English (Australia)',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ru': 'Russian'
        }
    
    async def check_text_with_languagetool(self, text: str, language: str = 'en-US') -> dict:
        """Check text using LanguageTool API."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'UnderLand-Grammar-Bot/2025.1 (Discord Bot)'
                }
                
                data = {
                    'text': text,
                    'language': language,
                    'enabledOnly': 'false'
                }
                
                async with session.post(
                    self.api_url, 
                    data=data, 
                    headers=headers,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'data': result,
                            'language': language
                        }
                    else:
                        logger.error(f"LanguageTool API error: {response.status}")
                        return {
                            'success': False,
                            'error': f"API returned status {response.status}"
                        }
        
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': "Request timed out"
            }
        except Exception as e:
            logger.error(f"LanguageTool API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_corrections(self, api_response: dict) -> list:
        """Format LanguageTool response into correction objects."""
        if not api_response.get('success') or not api_response['data'].get('matches'):
            return []
        
        corrections = []
        matches = api_response['data']['matches']
        
        for match in matches:
            # Extract error details
            context = match.get('context', {})
            error_text = context.get('text', '')
            offset = context.get('offset', 0)
            length = context.get('length', 0)
            
            # Get suggestions
            replacements = [r.get('value', '') for r in match.get('replacements', [])]
            
            # Categorize the issue
            rule = match.get('rule', {})
            issue_category = rule.get('category', {}).get('name', 'Unknown')
            issue_id = rule.get('id', 'unknown')
            
            # Map categories to readable names
            category_map = {
                'TYPOS': 'Spelling Error',
                'GRAMMAR': 'Grammar Error', 
                'PUNCTUATION': 'Punctuation',
                'CASING': 'Capitalization',
                'REDUNDANCY': 'Redundancy',
                'STYLE': 'Style',
                'COLLOQUIALISMS': 'Informal Language',
                'PLAIN_ENGLISH': 'Clarity',
                'SEMANTICS': 'Word Choice'
            }
            
            issue_type = category_map.get(issue_category, issue_category)
            
            correction = {
                'message': match.get('message', 'No description available'),
                'offset': match.get('offset', 0),
                'length': match.get('length', 0),
                'replacements': replacements[:5],  # Limit to 5 suggestions
                'issue_type': issue_type,
                'rule_category': issue_category,
                'rule_id': issue_id,
                'context_text': error_text,
                'context_offset': offset,
                'context_length': length
            }
            
            corrections.append(correction)
        
        return corrections
    
    @commands.command(name="grammar", aliases=["check", "spell"])
    async def grammar_check_prefix(self, ctx, *, text: str):
        """Check text for grammar and spelling errors using LanguageTool."""
        await self.perform_grammar_check(ctx, text, 'en-US', is_slash=False)
    
    @app_commands.command(name="grammar", description="Check text for grammar and spelling errors")
    @app_commands.describe(
        text="The text to check for grammar and spelling errors",
        language="Language code (default: en-US)"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="English (US)", value="en-US"),
        app_commands.Choice(name="English (UK)", value="en-GB"),
        app_commands.Choice(name="English (Canada)", value="en-CA"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="French", value="fr"),
        app_commands.Choice(name="Spanish", value="es"),
        app_commands.Choice(name="Italian", value="it")
    ])
    async def grammar_check_slash(
        self, 
        interaction: discord.Interaction, 
        text: str, 
        language: Optional[str] = "en-US"
    ):
        """Check text for grammar and spelling errors using LanguageTool."""
        await self.perform_grammar_check(interaction, text, language or 'en-US', is_slash=True)
    
    async def perform_grammar_check(self, ctx_or_interaction, text: str, language: str, is_slash: bool):
        """Perform the grammar check and display results."""
        # Validate text length
        if len(text) > 2000:
            error_msg = "❌ Text is too long! Please limit to 2000 characters."
            if is_slash:
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)
            return
        
        # Send "thinking" message
        if is_slash:
            await ctx_or_interaction.response.defer()
        else:
            async with ctx_or_interaction.typing():
                pass
        
        # Check with LanguageTool
        api_response = await self.check_text_with_languagetool(text, language)
        
        if not api_response['success']:
            error_embed = discord.Embed(
                title="❌ Grammar Check Failed",
                description=f"Unable to check your text: {api_response.get('error', 'Unknown error')}",
                color=discord.Color.red()
            )
            
            if is_slash:
                await ctx_or_interaction.followup.send(embed=error_embed)
            else:
                await ctx_or_interaction.send(embed=error_embed)
            return
        
        # Format corrections
        corrections = self.format_corrections(api_response)
        
        if not corrections:
            # No issues found
            embed = discord.Embed(
                title="✅ Excellent Writing!",
                description="No grammar or spelling issues found in your text.",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📝 Your Text",
                value=f"```{text[:500]}{'...' if len(text) > 500 else ''}```",
                inline=False
            )
            
            embed.add_field(
                name="🌍 Language",
                value=f"{self.languages.get(language, language)}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Statistics",
                value=f"• **Words:** {len(text.split())}\n• **Characters:** {len(text)}",
                inline=True
            )
            
            embed.set_footer(text="Powered by LanguageTool API • Keep up the great writing!")
            
            if is_slash:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return
        
        # Create interactive view for corrections
        view = GrammarView(text, corrections)
        embed = view.create_correction_embed()
        
        # Add summary information
        embed.add_field(
            name="📊 Summary",
            value=f"• **Issues Found:** {len(corrections)}\n• **Language:** {self.languages.get(language, language)}\n• **Text Length:** {len(text)} characters",
            inline=False
        )
        
        if is_slash:
            view.message = await ctx_or_interaction.followup.send(embed=embed, view=view)
        else:
            view.message = await ctx_or_interaction.send(embed=embed, view=view)
    
    @commands.command(name="quickfix", aliases=["qf"])
    async def quick_fix(self, ctx, *, text: str):
        """Quickly fix text and return the corrected version."""
        if len(text) > 1000:
            await ctx.send("❌ Text too long for quick fix! Use `?grammar` for longer texts.")
            return
        
        async with ctx.typing():
            api_response = await self.check_text_with_languagetool(text, 'en-US')
        
        if not api_response['success']:
            await ctx.send(f"❌ Quick fix failed: {api_response.get('error', 'Unknown error')}")
            return
        
        corrections = self.format_corrections(api_response)
        
        if not corrections:
            await ctx.send(f"✅ **No fixes needed!**\n```{text}```")
            return
        
        # Apply all corrections automatically
        corrected_text = text
        sorted_corrections = sorted(corrections, key=lambda x: x['offset'], reverse=True)
        
        for correction in sorted_corrections:
            if correction['replacements']:
                offset = correction['offset']
                length = correction['length']
                replacement = correction['replacements'][0]
                corrected_text = corrected_text[:offset] + replacement + corrected_text[offset + length:]
        
        embed = discord.Embed(
            title="🔧 Quick Fix Applied",
            description=f"Found and fixed {len(corrections)} issues",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Original",
            value=f"```{text}```",
            inline=False
        )
        
        embed.add_field(
            name="✨ Corrected",
            value=f"```{corrected_text}```", 
            inline=False
        )
        
        # Show what was fixed
        if len(corrections) <= 3:
            fixes = []
            for correction in corrections[:3]:
                fixes.append(f"• {correction['issue_type']}: {correction['message'][:50]}{'...' if len(correction['message']) > 50 else ''}")
            
            embed.add_field(
                name="🔍 Fixes Applied",
                value="\n".join(fixes),
                inline=False
            )
        
        embed.set_footer(text="Use ?grammar for interactive checking with more options")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="languages", aliases=["langs"])
    async def supported_languages(self, ctx):
        """Show supported languages for grammar checking."""
        embed = discord.Embed(
            title="🌍 Supported Languages",
            description="Languages available for grammar and spell checking",
            color=discord.Color.blue()
        )
        
        # Group languages nicely
        english_variants = [
            "🇺🇸 English (US) - `en-US`",
            "🇬🇧 English (UK) - `en-GB`", 
            "🇨🇦 English (Canada) - `en-CA`",
            "🇦🇺 English (Australia) - `en-AU`"
        ]
        
        other_languages = [
            "🇩🇪 German - `de`",
            "🇫🇷 French - `fr`",
            "🇪🇸 Spanish - `es`",
            "🇮🇹 Italian - `it`",
            "🇵🇹 Portuguese - `pt`",
            "🇳🇱 Dutch - `nl`",
            "🇷🇺 Russian - `ru`"
        ]
        
        embed.add_field(
            name="🔤 English Variants",
            value="\n".join(english_variants),
            inline=False
        )
        
        embed.add_field(
            name="🌐 Other Languages",
            value="\n".join(other_languages),
            inline=False
        )
        
        embed.add_field(
            name="💡 Usage",
            value="Use `/grammar` with language option or `?grammar` (defaults to English US)",
            inline=False
        )
        
        embed.set_footer(text="Powered by LanguageTool API • More languages may be added")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(GrammarCheckerCog(bot))
