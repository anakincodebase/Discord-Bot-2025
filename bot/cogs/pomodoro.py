"""
Pomodoro Timer functionality for the Discord bot.
Provides focus session management with customizable work/break intervals.

Author: Afnan Ahmed
Created: 2025
Description: Productivity timer system with participant management,
             customizable intervals, and interactive controls.
Features: Work/break cycles, participant tracking, 
          timer controls, session statistics.
License: MIT
"""

import asyncio
import logging
from typing import Dict, Set

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from discord import ButtonStyle, Embed

logger = logging.getLogger(__name__)

# Global storage for active pomodoro sessions
_active_pomodoros: Dict[int, 'PomodoroSession'] = {}

class PomodoroView(View):
    """View for Pomodoro session controls."""
    
    def __init__(self, session):
        super().__init__(timeout=None)
        self.session = session

    @discord.ui.button(label="Stop Session", style=ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop the current Pomodoro session."""
        if interaction.user not in self.session.participants:
            return await interaction.response.send_message("Only participants can stop this session.", ephemeral=True)
        self.session.stopped = True
        await interaction.response.edit_message(content="🛑 Pomodoro session stopped.", view=None)

class PomodoroSession:
    """Represents a Pomodoro focus session."""
    
    GIF_URL = "https://i.giphy.com/6XX4V0O8a0xdS.webp"

    def __init__(self, bot, channel, focus: float, brk: float, cycles: int):
        self.bot = bot
        self.channel = channel
        self.focus = int(focus * 60)  # Convert to seconds
        self.brk = int(brk * 60)      # Convert to seconds
        self.cycles = cycles
        self.participants: Set[discord.User] = set()
        self.stopped = False
        self.view = PomodoroView(self)

    async def run(self):
        """Run the complete Pomodoro session."""
        # Join phase
        join_embed = Embed(
            title="🍅 Pomodoro Session Starting!",
            description=f"React with ✅ to join!\nSession: **{self.focus // 60} min focus**, **{self.brk // 60} min break**, {self.cycles} cycles.\n_You have 30 seconds to join!_",
            color=0x5865F2
        )
        join_msg = await self.channel.send(embed=join_embed)
        await join_msg.add_reaction("✅")
        await asyncio.sleep(30)

        # Get participants
        try:
            join_msg = await self.channel.fetch_message(join_msg.id)
            for reaction in join_msg.reactions:
                if str(reaction.emoji) == "✅":
                    users = [u async for u in reaction.users() if not u.bot]
                    self.participants = set(users)
                    break
        except discord.NotFound:
            logger.warning("Join message was deleted")

        if not self.participants:
            return await self.channel.send("No one joined the Pomodoro session. Cancelled.")

        await self.channel.send("🍅 Pomodoro session is starting!\nParticipants: " + ", ".join(u.mention for u in self.participants))

        # Run cycles
        for i in range(1, self.cycles + 1):
            if self.stopped:
                break
            await self._phase(i, "Work", self.focus, True)
            if self.stopped or i == self.cycles:
                break
            await self._phase(i, "Break", self.brk, False)

        if not self.stopped:
            await self.channel.send("🎉 Pomodoro session complete! Great job!")
        _active_pomodoros.pop(self.channel.id, None)

    async def _phase(self, num: int, name: str, seconds: int, show_gif: bool):
        """Run a single phase (work or break) of the Pomodoro session."""
        title = f"🔔 Cycle {num}/{self.cycles} — {name}!"
        desc = "**Focus Time!**\nAlmost there, keep pushing! 🔥" if name == "Work" else "**Break Time!**\nRelax and recharge! 😌"
        embed = Embed(title=title, description=desc, color=0x43B581)
        if show_gif:
            embed.set_image(url=self.GIF_URL)
        
        try:
            msg = await self.channel.send(embed=embed, view=self.view)
        except discord.HTTPException as e:
            logger.error(f"Failed to send Pomodoro message: {e}")
            return

        while seconds > 0:
            if self.stopped:
                break
            mm, ss = divmod(seconds, 60)
            edit = Embed(title=title, description=f"{desc}\n\n`{mm:02}:{ss:02}`", color=0x43B581)
            if show_gif:
                edit.set_image(url=self.GIF_URL)
            
            try:
                await msg.edit(embed=edit, view=self.view)
            except discord.HTTPException as e:
                logger.error(f"Failed to edit Pomodoro message: {e}")
                break
                
            await asyncio.sleep(1)
            seconds -= 1

class PomodoroCog(commands.Cog):
    """Cog for Pomodoro timer functionality."""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pomodoro")
    async def pomodoro_prefix(self, ctx, focus: float = 25, brk: float = 5, cycles: int = 4):
        """Start a Pomodoro session (prefix command)."""
        if ctx.channel.id in _active_pomodoros:
            return await ctx.send("A Pomodoro session is already running in this channel.")
        
        session = PomodoroSession(self.bot, ctx.channel, focus, brk, cycles)
        _active_pomodoros[ctx.channel.id] = session
        await session.run()

    @app_commands.command(name="pomodoro", description="Start a Pomodoro session")
    @app_commands.describe(
        focus="Focus time in minutes (default: 25)",
        brk="Break time in minutes (default: 5)", 
        cycles="Number of cycles (default: 4)"
    )
    async def pomodoro_slash(self, interaction: discord.Interaction, focus: float = 25.0, brk: float = 5.0, cycles: int = 4):
        """Start a Pomodoro session (slash command)."""
        if interaction.channel_id in _active_pomodoros:
            return await interaction.response.send_message("A Pomodoro session is already running in this channel.", ephemeral=True)
        
        await interaction.response.defer()
        session = PomodoroSession(self.bot, interaction.channel, focus, brk, cycles)
        _active_pomodoros[interaction.channel_id] = session
        await session.run()

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(PomodoroCog(bot))
