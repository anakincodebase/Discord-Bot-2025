"""
Enhanced Help System - Cloud Deployment Version
Organized help system excluding AI and Music functionality for lightweight deployment.

Author: Afnan Ahmed
Created: 2025
Description: Professional help system for cloud deployment without resource-intensive features.
License: MIT
"""

import asyncio
import logging
from typing import Dict, List, Optional

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class HelpCategory:
    """Represents a category of commands with detailed information."""
    
    def __init__(self, name: str, emoji: str, description: str):
        self.name = name
        self.emoji = emoji
        self.description = description
        self.commands: List[Dict] = []
        self.features: List[str] = []
    
    def add_command(self, command: str, description: str, usage: str = "", examples: List[str] = None, 
                   aliases: List[str] = None, permissions: str = None):
        """Add a command to this category."""
        cmd_info = {
            "command": command,
            "description": description,
            "usage": usage,
            "examples": examples or [],
            "aliases": aliases or [],
            "permissions": permissions
        }
        self.commands.append(cmd_info)
    
    def add_feature(self, feature: str):
        """Add a feature description to this category."""
        self.features.append(feature)
    
    def get_command_count(self) -> int:
        """Get the number of commands in this category."""
        return len(self.commands)


class DeploymentHelpManager:
    """Manages help data for cloud deployment version."""
    
    def __init__(self):
        self.categories: Dict[str, HelpCategory] = {}
        self._initialize_deployment_help()
    
    def _initialize_deployment_help(self):
        """Initialize help categories for deployment version (no AI/Music)."""
        
        # 🎮 Fun & Games
        games = HelpCategory("Fun & Games", "🎮", "Interactive games and entertainment")
        games.add_command("hangman", "Play interactive word guessing game", "?hangman")
        games.add_command("tictactoe", "Challenge someone to Tic-Tac-Toe", "?tictactoe @user",
                         ["?tictactoe @friend"])
        games.add_command("trivia", "Answer random trivia questions (30s timer)", "?trivia")
        games.add_command("ship", "Calculate love compatibility between users", "?ship @user1 @user2",
                         ["?ship @alice @bob"])
        games.add_command("say", "Make the bot repeat your message", "?say <message>",
                         ["?say Hello world!"], permissions="Manage Messages")
        games.add_feature("🎯 Interactive game sessions")
        games.add_feature("⏱️ Timed challenges")
        games.add_feature("🏆 Score tracking")
        games.add_feature("🎲 Random trivia questions")
        self.categories["games"] = games
        
        # 😄 Social & Interaction
        social = HelpCategory("Social & Interaction", "😄", "Fun social commands with animations")
        social.add_command("bonk", "Bonk someone with animated reactions", "?bonk @user",
                          ["?bonk @friend"])
        social.add_command("kiss", "Send a sweet kiss with emojis", "?kiss @user")
        social.add_command("hug", "Give a warm hug with animations", "?hug @user")
        social.add_command("slap", "Dramatic slap with reactions", "?slap @user")
        social.add_command("yeet", "Launch someone into the void", "?yeet @user")
        social.add_command("facepalm", "Express disappointment dramatically", "?facepalm")
        social.add_command("rip", "Pay respects with memorial messages", "?rip @user")
        social.add_command("avatar", "Display user's profile picture", "?avatar @user")
        social.add_feature("🎭 Animated reactions")
        social.add_feature("💫 Interactive responses")
        social.add_feature("🎨 Rich embed displays")
        social.add_feature("😊 Emoji-rich interactions")
        self.categories["social"] = social
        
        # 📚 Dictionary & Learning
        education = HelpCategory("Dictionary & Learning", "📚", "Language learning and reference tools")
        education.add_command("def", "Get English word definitions", "?def <word>",
                             ["?def serendipity", "?def happiness"])
        education.add_command("associate", "Find related words and synonyms", "?associate <word>",
                             ["?associate happy"])
        education.add_feature("🧠 Vocabulary building tools")
        education.add_feature("📖 Dictionary definitions")
        education.add_feature("🔗 Word associations")
        education.add_feature("📝 Learning assistance")
        self.categories["education"] = education
        
        # ⏱️ Productivity & Tools
        productivity = HelpCategory("Productivity & Tools", "⏱️", "Focus and productivity enhancement")
        productivity.add_command("pomodoro", "Start focus session (25 min default)", "?pomodoro [duration]",
                                ["?pomodoro", "?pomodoro 30"])
        productivity.add_feature("🎯 Customizable work/break intervals")
        productivity.add_feature("📊 Progress tracking")
        productivity.add_feature("⏰ Smart notifications")
        productivity.add_feature("🔔 Session reminders")
        self.categories["productivity"] = productivity
        
        # 🛠️ Moderation & Admin
        moderation = HelpCategory("Moderation & Admin", "🛠️", "Server management and moderation tools")
        moderation.add_command("mute", "Mute a user temporarily", "?mute @user [reason]",
                              ["?mute @spammer Being disruptive"], permissions="Manage Messages")
        moderation.add_command("unmute", "Remove mute from user", "?unmute @user",
                              ["?unmute @user"], permissions="Manage Messages")
        moderation.add_command("ban", "Ban user from server", "?ban @user [reason]",
                              ["?ban @troublemaker Harassment"], permissions="Ban Members")
        moderation.add_command("kick", "Kick user from server", "?kick @user [reason]",
                              ["?kick @user Breaking rules"], permissions="Kick Members")
        moderation.add_command("purge", "Delete messages in bulk", "?purge <amount>",
                              ["?purge 10", "?purge 50"], permissions="Manage Messages")
        moderation.add_feature("🔒 Role-based permissions")
        moderation.add_feature("⚡ Bulk operations")
        moderation.add_feature("🛡️ Security controls")
        moderation.add_feature("📝 Reason logging")
        self.categories["moderation"] = moderation
        
        # 🌐 Server & Utility
        utility = HelpCategory("Server & Utility", "🌐", "Server information and utility commands")
        utility.add_command("whois", "Get detailed user information", "?whois @user",
                           ["?whois @friend", "?whois"])
        utility.add_command("poll", "Create interactive polls", "?poll <question> <option1> <option2>",
                           ["?poll 'Pizza or burgers?' Pizza Burgers"])
        utility.add_command("ping", "Check bot latency and status", "?ping")
        utility.add_command("status", "Show detailed bot status", "?status")
        utility.add_command("help", "Show this comprehensive help", "?help", aliases=["h"])
        utility.add_command("commands", "Quick command reference list", "?commands", aliases=["cmds"])
        utility.add_feature("📊 Server statistics")
        utility.add_feature("🔍 User information")
        utility.add_feature("📱 Interactive polls")
        utility.add_feature("⚡ Performance monitoring")
        self.categories["utility"] = utility
        
        # 🎭 Script Sessions
        scripts = HelpCategory("Script Sessions", "🎭", "Interactive story and roleplay features")
        scripts.add_command("script", "Start interactive script session", "?script",
                           ["?script"])
        scripts.add_feature("📚 Interactive storytelling")
        scripts.add_feature("🎭 Character roleplay")
        scripts.add_feature("🎬 Script-based adventures")
        scripts.add_feature("👥 Group participation")
        self.categories["scripts"] = scripts
    
    def get_category(self, category_key: str) -> Optional[HelpCategory]:
        """Get a specific category."""
        return self.categories.get(category_key)
    
    def get_all_categories(self) -> List[HelpCategory]:
        """Get all categories in order."""
        order = ["games", "social", "education", "productivity", "moderation", "utility", "scripts"]
        return [self.categories[key] for key in order if key in self.categories]
    
    def get_total_commands(self) -> int:
        """Get total number of commands across all categories."""
        return sum(cat.get_command_count() for cat in self.categories.values())
    
    def search_commands(self, query: str) -> List[tuple]:
        """Search for commands matching a query."""
        results = []
        query_lower = query.lower()
        
        for cat_key, category in self.categories.items():
            for cmd in category.commands:
                if (query_lower in cmd["command"].lower() or 
                    query_lower in cmd["description"].lower() or
                    any(query_lower in alias.lower() for alias in cmd["aliases"])):
                    results.append((category, cmd))
        
        return results


class HelpView(discord.ui.View):
    """Interactive view for paginated help system."""
    
    def __init__(self, ctx, help_manager: DeploymentHelpManager):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.help_manager = help_manager
        self.categories = help_manager.get_all_categories()
        self.current_page = 0
        self.message = None
        
        self.add_item(HelpDropdown(self))
    
    async def send_initial_message(self):
        """Send the initial help message."""
        embed = self.create_overview_embed()
        self.message = await self.ctx.send(embed=embed, view=self)
    
    def create_overview_embed(self) -> discord.Embed:
        """Create the main overview embed."""
        embed = discord.Embed(
            title="🌙 UnderLand Bot - Cloud Edition",
            description="**Professional Discord bot optimized for 24/7 deployment**\n\n"
                       "🎯 **Quick Start:** Use the dropdown below to explore features\n"
                       "🔍 **Search:** Type `?help <command>` for specific help\n"
                       "📋 **Quick List:** Use `?commands` for a compact view",
            color=0x2F3136
        )
        
        # Add statistics
        total_commands = self.help_manager.get_total_commands()
        embed.add_field(
            name="📊 Bot Information",
            value=f"**{total_commands} Commands** across **{len(self.categories)} Categories**\n"
                  f"**Prefixes:** `?`, `!`, `n!`, `nz!`\n"
                  f"**Status:** ✅ Optimized for cloud deployment",
            inline=False
        )
        
        # Add category overview
        category_list = []
        for cat in self.categories:
            count = cat.get_command_count()
            count_text = f"{count} commands" if count > 0 else "Features"
            category_list.append(f"{cat.emoji} **{cat.name}** - {count_text}")
        
        embed.add_field(
            name="📂 Available Categories",
            value="\n".join(category_list),
            inline=False
        )
        
        embed.add_field(
            name="🚀 Popular Commands",
            value="`?hangman` • `?trivia` • `?ping` • `?poll` • `?def`",
            inline=False
        )
        
        embed.add_field(
            name="🌟 Deployment Features",
            value="• ⚡ Lightweight & Fast\n"
                  "• 🔄 24/7 Uptime Ready\n"
                  "• 📱 Full Discord Integration\n"
                  "• 🛡️ Secure & Stable",
            inline=False
        )
        
        embed.set_footer(text="Created by Afnan Ahmed • Use dropdown to explore categories")
        
        return embed
    
    def create_category_embed(self, category: HelpCategory) -> discord.Embed:
        """Create an embed for a specific category."""
        embed = discord.Embed(
            title=f"{category.emoji} {category.name}",
            description=f"**{category.description}**\n\n",
            color=0x5865F2
        )
        
        # Add commands
        if category.commands:
            command_text = []
            for cmd in category.commands:
                cmd_line = f"**`{cmd['command']}`** - {cmd['description']}"
                if cmd['aliases']:
                    cmd_line += f" (aliases: {', '.join(f'`{alias}`' for alias in cmd['aliases'])})"
                if cmd['permissions']:
                    cmd_line += f"\n   *Requires: {cmd['permissions']}*"
                command_text.append(cmd_line)
            
            embed.add_field(
                name=f"📋 Commands ({len(category.commands)})",
                value="\n\n".join(command_text),
                inline=False
            )
        
        # Add features
        if category.features:
            embed.add_field(
                name="✨ Features",
                value="\n".join(category.features),
                inline=False
            )
        
        # Add usage examples
        examples = []
        for cmd in category.commands[:2]:
            if cmd['examples']:
                examples.extend(cmd['examples'][:2])
        
        if examples:
            embed.add_field(
                name="💡 Example Usage",
                value="\n".join(f"`{ex}`" for ex in examples),
                inline=False
            )
        
        embed.set_footer(text=f"Use ?help <command> for detailed information")
        
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the user can interact with this view."""
        return interaction.user == self.ctx.author
    
    async def on_timeout(self):
        """Handle view timeout."""
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass


class HelpDropdown(discord.ui.Select):
    """Dropdown for selecting help categories."""
    
    def __init__(self, help_view: HelpView):
        self.help_view = help_view
        
        options = [
            discord.SelectOption(
                label="📖 Overview",
                description="Main help page with all categories",
                value="overview",
                emoji="📖"
            )
        ]
        
        for i, category in enumerate(help_view.categories):
            options.append(
                discord.SelectOption(
                    label=category.name,
                    description=category.description[:100],  # Discord limit
                    value=str(i),
                    emoji=category.emoji
                )
            )
        
        super().__init__(
            placeholder="🔍 Select a category to explore...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle dropdown selection."""
        if self.values[0] == "overview":
            embed = self.help_view.create_overview_embed()
        else:
            page_num = int(self.values[0])
            category = self.help_view.categories[page_num]
            embed = self.help_view.create_category_embed(category)
        
        await interaction.response.edit_message(embed=embed, view=self.help_view)


class EnhancedHelpCog(commands.Cog):
    """Enhanced help system for cloud deployment."""
    
    def __init__(self, bot):
        self.bot = bot
        self.help_manager = DeploymentHelpManager()
        
        # Remove default help command
        self.bot.remove_command('help')
    
    @commands.command(name="help", aliases=["h"])
    async def enhanced_help(self, ctx, *, query: Optional[str] = None):
        """Show comprehensive help information for all bot features."""
        
        if query:
            await self._handle_specific_help(ctx, query)
        else:
            view = HelpView(ctx, self.help_manager)
            await view.send_initial_message()
    
    async def _handle_specific_help(self, ctx, query: str):
        """Handle help for a specific command or category."""
        query_lower = query.lower()
        
        # Check if it's a category name
        for cat_key, category in self.help_manager.categories.items():
            if query_lower in category.name.lower():
                embed = self._create_specific_category_embed(category)
                await ctx.send(embed=embed)
                return
        
        # Search for commands
        results = self.help_manager.search_commands(query)
        
        if not results:
            embed = discord.Embed(
                title="❓ Command Not Found",
                description=f"Could not find help for `{query}`.\n\n"
                           "💡 **Suggestions:**\n"
                           "• Use `?help` for the main menu\n"
                           "• Use `?commands` for a quick list\n"
                           "• Check your spelling",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        if len(results) == 1:
            category, command = results[0]
            embed = self._create_command_embed(category, command)
        else:
            embed = self._create_search_results_embed(query, results)
        
        await ctx.send(embed=embed)
    
    def _create_specific_category_embed(self, category: HelpCategory) -> discord.Embed:
        """Create a detailed embed for a specific category."""
        embed = discord.Embed(
            title=f"{category.emoji} {category.name} - Detailed Help",
            description=category.description,
            color=0x5865F2
        )
        
        if category.commands:
            for cmd in category.commands[:10]:  # Limit to prevent embed size issues
                field_value = f"**Description:** {cmd['description']}\n"
                if cmd['usage']:
                    field_value += f"**Usage:** `{cmd['usage']}`\n"
                if cmd['aliases']:
                    field_value += f"**Aliases:** {', '.join(f'`{alias}`' for alias in cmd['aliases'])}\n"
                if cmd['examples']:
                    field_value += f"**Examples:**\n{chr(10).join(f'• `{ex}`' for ex in cmd['examples'][:2])}\n"
                if cmd['permissions']:
                    field_value += f"**Required Permission:** {cmd['permissions']}\n"
                
                embed.add_field(
                    name=f"`{cmd['command']}`",
                    value=field_value,
                    inline=False
                )
        
        if category.features:
            embed.add_field(
                name="✨ Features",
                value="\n".join(category.features),
                inline=False
            )
        
        return embed
    
    def _create_command_embed(self, category: HelpCategory, command: dict) -> discord.Embed:
        """Create a detailed embed for a specific command."""
        embed = discord.Embed(
            title=f"📖 Command Help: `{command['command']}`",
            description=command['description'],
            color=0x00FF7F
        )
        
        if command['usage']:
            embed.add_field(name="📝 Usage", value=f"`{command['usage']}`", inline=False)
        
        if command['aliases']:
            embed.add_field(
                name="🔗 Aliases", 
                value=", ".join(f"`{alias}`" for alias in command['aliases']), 
                inline=True
            )
        
        if command['permissions']:
            embed.add_field(name="🔒 Required Permission", value=command['permissions'], inline=True)
        
        if command['examples']:
            embed.add_field(
                name="💡 Examples",
                value="\n".join(f"• `{ex}`" for ex in command['examples']),
                inline=False
            )
        
        embed.add_field(name="📂 Category", value=f"{category.emoji} {category.name}", inline=True)
        
        return embed
    
    def _create_search_results_embed(self, query: str, results: List[tuple]) -> discord.Embed:
        """Create an embed showing multiple search results."""
        embed = discord.Embed(
            title=f"🔍 Search Results for '{query}'",
            description=f"Found {len(results)} matching commands:",
            color=0xFFD700
        )
        
        for category, command in results[:8]:  # Limit to prevent embed size issues
            embed.add_field(
                name=f"`{command['command']}`",
                value=f"**{command['description']}**\n*Category: {category.emoji} {category.name}*",
                inline=False
            )
        
        if len(results) > 8:
            embed.set_footer(text=f"Showing first 8 of {len(results)} results.")
        
        return embed
    
    @commands.command(name="commands", aliases=["cmds", "commandlist"])
    async def quick_commands(self, ctx):
        """Show a quick reference list of all available commands."""
        embed = discord.Embed(
            title="📋 Quick Commands Reference",
            description="All available bot commands at a glance",
            color=0x36393F
        )
        
        for category in self.help_manager.get_all_categories():
            if category.commands:
                cmd_list = [cmd["command"] for cmd in category.commands]
                embed.add_field(
                    name=f"{category.emoji} {category.name}",
                    value=", ".join(f"`{cmd}`" for cmd in cmd_list),
                    inline=False
                )
        
        total_commands = self.help_manager.get_total_commands()
        embed.set_footer(text=f"Total: {total_commands} commands • Use ?help <command> for details")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="about", aliases=["info", "botstats"])
    async def about_bot(self, ctx):
        """Show information about the bot."""
        embed = discord.Embed(
            title="🤖 About UnderLand Bot",
            description="Professional Discord bot optimized for 24/7 cloud deployment",
            color=0x7289DA
        )
        
        # Bot statistics
        total_commands = self.help_manager.get_total_commands()
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Commands:** {total_commands}\n"
                  f"**Servers:** {len(self.bot.guilds)}\n"
                  f"**Users:** {member_count:,}\n"
                  f"**Latency:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        # Features
        embed.add_field(
            name="✨ Features",
            value="• 🎮 Interactive games\n"
                  "• 😄 Social commands\n"
                  "• 📚 Dictionary tools\n"
                  "• ⏱️ Productivity features\n"
                  "• 🛠️ Moderation tools\n"
                  "• 🎭 Script sessions",
            inline=True
        )
        
        # Deployment info
        embed.add_field(
            name="🚀 Deployment",
            value="• ⚡ Lightweight design\n"
                  "• 🔄 24/7 uptime ready\n"
                  "• ☁️ Cloud optimized\n"
                  "• 🛡️ Secure & stable",
            inline=True
        )
        
        embed.set_footer(text="Created by Afnan Ahmed • Use ?help for command info")
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the enhanced help cog."""
    await bot.add_cog(EnhancedHelpCog(bot))
