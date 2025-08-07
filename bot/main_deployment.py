#!/usr/bin/env python3
"""
UnderLand Discord Bot - Cloud Deployment Version
Professional Discord bot optimized for 24/7 cloud deployment.

Author: Afnan Ahmed
Created: 2025
Description: Lightweight Discord bot for cloud deployment without AI/Music dependencies.
             Includes fun commands, moderation tools, utilities, and interactive features.
Features: Fun games, moderation commands, utility tools, pomodoro timer,
          script sessions, and comprehensive help system.
License: MIT
"""

import asyncio
import logging
import os
from pathlib import Path
import difflib

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.config_deployment import DeploymentConfig
from bot.cogs.fun import FunCog
from bot.cogs.moderation import ModerationCog
from bot.cogs.utils import UtilsCog, Dictionary
from bot.cogs.pomodoro import PomodoroCog
from bot.cogs.enhanced_help_deployment import EnhancedHelpCog
from bot.cogs.script_session import ScriptSessionCog
from bot.database.db import init_db

# Setup logging with UTF-8 encoding for cloud deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only console logging for cloud deployment
    ]
)
logger = logging.getLogger(__name__)

class UnderLandCloudBot(commands.Bot):
    """Main bot class optimized for cloud deployment."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=["?", "!", "n!", "nz!"],
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.config = DeploymentConfig()
        
    async def setup_hook(self):
        """Hook called when the bot is starting up."""
        logger.info("🚀 Starting UnderLand Cloud Bot...")
        
        # Initialize database
        await init_db()
        
        # Load deployment-safe cogs
        await self.load_deployment_cogs()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")
    
    async def load_deployment_cogs(self):
        """Load only cloud-deployment compatible cogs."""
        deployment_cogs = [
            FunCog,
            ModerationCog,
            UtilsCog,
            Dictionary,
            PomodoroCog,
            EnhancedHelpCog,
            ScriptSessionCog
        ]
        
        for cog in deployment_cogs:
            try:
                await self.add_cog(cog(self))
                logger.info(f"✅ Loaded {cog.__name__}")
            except Exception as e:
                logger.error(f"❌ Failed to load {cog.__name__}: {e}")
        
        logger.info(f"📋 Registered {len(self.commands)} commands")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"🌟 {self.user} is online and ready!")
        
        # Set bot status
        member_count = sum(guild.member_count for guild in self.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} members across {len(self.guilds)} servers"
        )
        await self.change_presence(
            activity=activity,
            status=discord.Status.online
        )
        
        logger.info(f"📊 Serving {member_count} members across {len(self.guilds)} guilds")
    
    async def on_guild_join(self, guild):
        """Handle bot joining a new guild."""
        logger.info(f"📥 Joined guild: {guild.name} (ID: {guild.id})")
        
        # Update status
        member_count = sum(g.member_count for g in self.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} members across {len(self.guilds)} servers"
        )
        await self.change_presence(activity=activity)
    
    async def on_guild_remove(self, guild):
        """Handle bot leaving a guild."""
        logger.info(f"📤 Left guild: {guild.name} (ID: {guild.id})")
        
        # Update status
        member_count = sum(g.member_count for g in self.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} members across {len(self.guilds)} servers"
        )
        await self.change_presence(activity=activity)
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check bot latency and status."""
        latency = round(self.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📡 Latency",
            value=f"`{latency}ms`",
            inline=True
        )
        embed.add_field(
            name="🌐 Status",
            value="✅ Online",
            inline=True
        )
        embed.add_field(
            name="🏠 Guilds",
            value=f"`{len(self.guilds)}`",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="status")
    async def status(self, ctx):
        """Show detailed bot status information."""
        embed = discord.Embed(
            title="🤖 UnderLand Status",
            color=discord.Color.blue()
        )
        
        # Basic stats
        member_count = sum(guild.member_count for guild in self.guilds)
        embed.add_field(
            name="📊 Statistics",
            value=f"🏠 **Guilds:** {len(self.guilds)}\n"
                  f"👥 **Members:** {member_count:,}\n"
                  f"⚡ **Latency:** {round(self.latency * 1000)}ms",
            inline=False
        )
        
        # Features
        embed.add_field(
            name="🎮 Available Features",
            value="🎲 **Games:** Hangman, Trivia, TicTacToe\n"
                  f"🛠️ **Utilities:** Dictionary, Avatar, Polls\n"
                  f"🎯 **Productivity:** Pomodoro Timer\n"
                  f"🎭 **Interactive:** Script Sessions\n"
                  f"🔨 **Moderation:** Basic mod tools",
            inline=False
        )
        
        embed.set_footer(text="Optimized for 24/7 cloud deployment")
        await ctx.send(embed=embed)
    
    async def on_command_error(self, ctx, error):
        """Enhanced error handling with helpful suggestions."""
        if isinstance(error, commands.CommandNotFound):
            attempted_command = ctx.invoked_with.lower()
            
            # Available commands for suggestions
            available_commands = [
                'help', 'ping', 'status', 'hangman', 'trivia', 'tictactoe', 
                'ship', 'bonk', 'hug', 'kiss', 'slap', 'def', 'whois', 
                'avatar', 'say', 'mute', 'ban', 'kick', 'purge', 'pomodoro', 
                'poll', 'script'
            ]
            
            closest_matches = difflib.get_close_matches(
                attempted_command, available_commands, n=3, cutoff=0.6
            )
            
            if closest_matches:
                embed = discord.Embed(
                    title="❓ Command Not Found",
                    description=f"🤔 `{attempted_command}` isn't available.",
                    color=discord.Color.orange()
                )
                
                suggestions = "\n".join([f"• `?{cmd}`" for cmd in closest_matches])
                embed.add_field(
                    name="💡 Did you mean?",
                    value=suggestions,
                    inline=False
                )
                
                embed.add_field(
                    name="📚 Need Help?",
                    value="Type `?help` to see all commands!",
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❓ Command Not Found",
                    description=f"🤔 `{attempted_command}` isn't a valid command.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📚 Get Help",
                    value="Type `?help` to see all available commands!",
                    inline=False
                )
                await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="⚠️ Missing Arguments",
                description="You're missing required arguments for this command.",
                color=discord.Color.yellow()
            )
            embed.add_field(
                name="💡 Tip",
                value="Try `?help <command>` for usage examples.",
                inline=False
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Missing Permissions",
                description="You don't have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="🤖 Bot Missing Permissions",
                description="I don't have the required permissions for this command.",
                color=discord.Color.red()
            )
            missing_perms = ", ".join(error.missing_permissions)
            embed.add_field(
                name="Required Permissions",
                value=f"`{missing_perms}`",
                inline=False
            )
            await ctx.send(embed=embed)
        
        else:
            logger.error(f"Command error in {ctx.command}: {error}")
            embed = discord.Embed(
                title="❌ Command Error",
                description="Something went wrong while executing this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def main():
    """Main function to run the bot."""
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN environment variable is required!")
        return
    
    # Create and run bot
    bot = UnderLandCloudBot()
    
    try:
        logger.info("🔐 Starting bot with token...")
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token!")
    except KeyboardInterrupt:
        logger.info("🛑 Bot shutting down...")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
