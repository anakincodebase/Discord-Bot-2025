#!/usr/bin/env python3
"""
Event Creation and Management Cog
Provides comprehensive event creation and management functionality for Discord servers.

Features:
- Create events with /createevent or ?createevent
- Set event title, description, date, time, and duration
- RSVP system for participants
- Event reminders and notifications
- List and manage upcoming events
- Event cancellation and modification

Author: Afnan Ahmed
Created: 2025
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import re

import discord
from discord.ext import commands, tasks
from discord import app_commands

logger = logging.getLogger(__name__)

class EventData:
    """Class to manage event data structure."""
    
    def __init__(self, event_id: str, title: str, description: str, 
                 creator_id: int, guild_id: int, channel_id: int,
                 start_time: datetime, duration_minutes: int = 60):
        self.event_id = event_id
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.created_at = datetime.utcnow()
        self.participants: List[int] = []
        self.maybe_participants: List[int] = []
        self.not_attending: List[int] = []
        self.is_cancelled = False
        self.reminder_sent = False
        self.discord_event_id: Optional[int] = None  # Discord native event ID
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for storage."""
        return {
            'event_id': self.event_id,
            'title': self.title,
            'description': self.description,
            'creator_id': self.creator_id,
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'start_time': self.start_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat(),
            'participants': self.participants,
            'maybe_participants': self.maybe_participants,
            'not_attending': self.not_attending,
            'is_cancelled': self.is_cancelled,
            'reminder_sent': self.reminder_sent,
            'discord_event_id': self.discord_event_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventData':
        """Create event from dictionary."""
        event = cls(
            event_id=data['event_id'],
            title=data['title'],
            description=data['description'],
            creator_id=data['creator_id'],
            guild_id=data['guild_id'],
            channel_id=data['channel_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            duration_minutes=data['duration_minutes']
        )
        event.created_at = datetime.fromisoformat(data['created_at'])
        event.participants = data.get('participants', [])
        event.maybe_participants = data.get('maybe_participants', [])
        event.not_attending = data.get('not_attending', [])
        event.is_cancelled = data.get('is_cancelled', False)
        event.reminder_sent = data.get('reminder_sent', False)
        event.discord_event_id = data.get('discord_event_id')
        return event

class EventView(discord.ui.View):
    """Interactive view for event RSVP management."""
    
    def __init__(self, event_data: EventData, bot: commands.Bot):
        super().__init__(timeout=None)
        self.event_data = event_data
        self.bot = bot
    
    @discord.ui.button(label="✅ Attending", style=discord.ButtonStyle.green, custom_id="attending")
    async def attending_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle attending button click."""
        user_id = interaction.user.id
        
        # Remove from other lists
        if user_id in self.event_data.maybe_participants:
            self.event_data.maybe_participants.remove(user_id)
        if user_id in self.event_data.not_attending:
            self.event_data.not_attending.remove(user_id)
        
        # Add to attending if not already there
        if user_id not in self.event_data.participants:
            self.event_data.participants.append(user_id)
            await interaction.response.send_message("✅ You're now marked as attending!", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ You're already marked as attending!", ephemeral=True)
        
        # Update the embed
        cog = self.bot.get_cog('EventsCog')
        if cog:
            await cog.save_events()
            embed = await cog.create_event_embed(self.event_data)
            await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="❓ Maybe", style=discord.ButtonStyle.grey, custom_id="maybe")
    async def maybe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle maybe button click."""
        user_id = interaction.user.id
        
        # Remove from other lists
        if user_id in self.event_data.participants:
            self.event_data.participants.remove(user_id)
        if user_id in self.event_data.not_attending:
            self.event_data.not_attending.remove(user_id)
        
        # Add to maybe if not already there
        if user_id not in self.event_data.maybe_participants:
            self.event_data.maybe_participants.append(user_id)
            await interaction.response.send_message("❓ You're now marked as maybe attending!", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ You're already marked as maybe attending!", ephemeral=True)
        
        # Update the embed
        cog = self.bot.get_cog('EventsCog')
        if cog:
            await cog.save_events()
            embed = await cog.create_event_embed(self.event_data)
            await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="❌ Not Attending", style=discord.ButtonStyle.red, custom_id="not_attending")
    async def not_attending_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle not attending button click."""
        user_id = interaction.user.id
        
        # Remove from other lists
        if user_id in self.event_data.participants:
            self.event_data.participants.remove(user_id)
        if user_id in self.event_data.maybe_participants:
            self.event_data.maybe_participants.remove(user_id)
        
        # Add to not attending if not already there
        if user_id not in self.event_data.not_attending:
            self.event_data.not_attending.append(user_id)
            await interaction.response.send_message("❌ You're now marked as not attending!", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ You're already marked as not attending!", ephemeral=True)
        
        # Update the embed
        cog = self.bot.get_cog('EventsCog')
        if cog:
            await cog.save_events()
            embed = await cog.create_event_embed(self.event_data)
            await interaction.edit_original_response(embed=embed, view=self)

class EventsCog(commands.Cog):
    """Cog for event creation and management functionality."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.events: Dict[str, EventData] = {}
        self.events_file = "bot_events.json"
        
        # Load existing events
        asyncio.create_task(self.load_events())
        
        # Start reminder checker
        self.check_reminders.start()
    
    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.check_reminders.cancel()
    
    async def load_events(self):
        """Load events from storage."""
        try:
            with open(self.events_file, 'r') as f:
                data = json.load(f)
                for event_id, event_data in data.items():
                    self.events[event_id] = EventData.from_dict(event_data)
            logger.info(f"Loaded {len(self.events)} events")
        except FileNotFoundError:
            logger.info("No existing events file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading events: {e}")
    
    async def save_events(self):
        """Save events to storage."""
        try:
            data = {event_id: event.to_dict() for event_id, event in self.events.items()}
            with open(self.events_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving events: {e}")
    
    def generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Parse date and time strings into datetime object."""
        try:
            # Common date formats
            date_formats = [
                "%Y-%m-%d",      # 2025-12-25
                "%m/%d/%Y",      # 12/25/2025
                "%d/%m/%Y",      # 25/12/2025
                "%m-%d-%Y",      # 12-25-2025
                "%d-%m-%Y",      # 25-12-2025
            ]
            
            # Common time formats
            time_formats = [
                "%H:%M",         # 14:30
                "%I:%M %p",      # 2:30 PM
                "%I:%M%p",       # 2:30PM
                "%H.%M",         # 14.30
            ]
            
            parsed_date = None
            for date_fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, date_fmt).date()
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                return None
            
            parsed_time = None
            for time_fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str, time_fmt).time()
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                return None
            
            return datetime.combine(parsed_date, parsed_time)
        
        except Exception as e:
            logger.error(f"Error parsing datetime: {e}")
            return None
    
    async def create_discord_event(self, guild: discord.Guild, event_data: EventData) -> Optional[discord.ScheduledEvent]:
        """Create a Discord native scheduled event."""
        try:
            # Check if bot has permission to manage events
            if not guild.me.guild_permissions.manage_events:
                logger.warning(f"Bot lacks 'Manage Events' permission in guild {guild.id}")
                return None
            
            # Create the Discord scheduled event
            discord_event = await guild.create_scheduled_event(
                name=event_data.title,
                description=event_data.description,
                start_time=event_data.start_time,
                end_time=event_data.start_time + timedelta(minutes=event_data.duration_minutes),
                entity_type=discord.EntityType.external,
                location="Discord Server Event",
                privacy_level=discord.PrivacyLevel.guild_only
            )
            
            logger.info(f"Created Discord event: {discord_event.id} for bot event: {event_data.event_id}")
            return discord_event
            
        except discord.Forbidden:
            logger.error(f"Missing permissions to create events in guild {guild.id}")
            return None
        except discord.HTTPException as e:
            logger.error(f"HTTP error creating Discord event: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Discord event: {e}")
            return None

    async def create_event_embed(self, event: EventData, discord_event: Optional[discord.ScheduledEvent] = None) -> discord.Embed:
        """Create embed for event display."""
        embed = discord.Embed(
            title=f"📅 {event.title}",
            description=event.description,
            color=discord.Color.blue() if not event.is_cancelled else discord.Color.red()
        )
        
        # Event details
        embed.add_field(
            name="🕒 Date & Time",
            value=f"**Start:** {event.start_time.strftime('%Y-%m-%d at %H:%M UTC')}\n"
                  f"**Duration:** {event.duration_minutes} minutes",
            inline=False
        )
        
        # Creator info
        creator = self.bot.get_user(event.creator_id)
        creator_name = creator.display_name if creator else "Unknown User"
        embed.add_field(
            name="👤 Created by",
            value=creator_name,
            inline=True
        )
        
        # Event ID and Discord integration
        embed.add_field(
            name="🆔 Event ID",
            value=f"`{event.event_id}`",
            inline=True
        )
        
        # Discord Event Status
        if event.discord_event_id:
            embed.add_field(
                name="🌐 Discord Event",
                value="✅ Created in server events",
                inline=True
            )
        else:
            embed.add_field(
                name="🌐 Discord Event",
                value="❌ Failed to create (check permissions)",
                inline=True
            )
        
        # RSVP counts
        attending_count = len(event.participants)
        maybe_count = len(event.maybe_participants)
        not_attending_count = len(event.not_attending)
        
        rsvp_text = f"✅ **Attending:** {attending_count}\n"
        rsvp_text += f"❓ **Maybe:** {maybe_count}\n"
        rsvp_text += f"❌ **Not Attending:** {not_attending_count}"
        
        embed.add_field(
            name="📊 RSVP Status",
            value=rsvp_text,
            inline=False
        )
        
        # Status
        if event.is_cancelled:
            embed.add_field(
                name="⚠️ Status",
                value="**CANCELLED**",
                inline=False
            )
        
        # Time until event
        time_until = event.start_time - datetime.utcnow()
        if time_until.total_seconds() > 0:
            days = time_until.days
            hours, remainder = divmod(time_until.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            time_text = []
            if days > 0:
                time_text.append(f"{days} day{'s' if days != 1 else ''}")
            if hours > 0:
                time_text.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes > 0:
                time_text.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            
            if time_text:
                embed.add_field(
                    name="⏰ Time Remaining",
                    value=" ".join(time_text),
                    inline=False
                )
        
        embed.set_footer(text=f"Created on {event.created_at.strftime('%Y-%m-%d at %H:%M UTC')}")
        return embed
    
    @commands.hybrid_command(name="createevent", description="Create a new event")
    @app_commands.describe(
        title="Event title",
        description="Event description",
        date="Event date (YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY)",
        time="Event time (HH:MM, H:MM AM/PM)",
        duration="Duration in minutes (default: 60)"
    )
    async def create_event(self, ctx: commands.Context, title: str, description: str, 
                          date: str, time: str, duration: int = 60):
        """Create a new event with the specified details."""
        
        # Parse datetime
        event_datetime = self.parse_datetime(date, time)
        if not event_datetime:
            embed = discord.Embed(
                title="❌ Invalid Date/Time",
                description="Please use valid date and time formats:",
                color=discord.Color.red()
            )
            embed.add_field(
                name="📅 Date Formats",
                value="• `YYYY-MM-DD` (2025-12-25)\n"
                      "• `MM/DD/YYYY` (12/25/2025)\n"
                      "• `DD/MM/YYYY` (25/12/2025)",
                inline=False
            )
            embed.add_field(
                name="🕒 Time Formats",
                value="• `HH:MM` (14:30)\n"
                      "• `H:MM AM/PM` (2:30 PM)",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Check if event is in the past
        if event_datetime < datetime.utcnow():
            embed = discord.Embed(
                title="❌ Invalid Date",
                description="Cannot create events in the past!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Validate duration
        if duration < 1 or duration > 1440:  # 1 minute to 24 hours
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Duration must be between 1 and 1440 minutes (24 hours).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Create event
        event_id = self.generate_event_id()
        event = EventData(
            event_id=event_id,
            title=title,
            description=description,
            creator_id=ctx.author.id,
            guild_id=ctx.guild.id,
            channel_id=ctx.channel.id,
            start_time=event_datetime,
            duration_minutes=duration
        )
        
        # Store event
        self.events[event_id] = event
        
        # Create Discord native event
        discord_event = await self.create_discord_event(ctx.guild, event)
        if discord_event:
            event.discord_event_id = discord_event.id
        
        await self.save_events()
        
        # Create embed and view
        embed = await self.create_event_embed(event, discord_event)
        view = EventView(event, self.bot)
        
        # Create success message
        success_message = f"✅ **Event Created Successfully!**\n\n"
        if discord_event:
            success_message += f"📅 **Discord Event:** Created in server events\n"
            success_message += f"🔗 **Event Link:** [View in Discord Events](https://discord.com/events/{ctx.guild.id}/{discord_event.id})\n"
        else:
            success_message += f"⚠️ **Note:** Could not create Discord server event (missing permissions)\n"
        success_message += f"🆔 **Bot Event ID:** `{event_id}`\n"
        success_message += f"⏰ **Reminders:** Will be sent 30 minutes before the event"
        
        # Send event message
        await ctx.send(success_message)
        await ctx.send(embed=embed, view=view)
        
        logger.info(f"Event created: {event_id} - {title} by {ctx.author}")
    
    @commands.hybrid_command(name="events", description="List upcoming events")
    async def list_events(self, ctx: commands.Context):
        """List all upcoming events in the server."""
        guild_events = [
            event for event in self.events.values() 
            if event.guild_id == ctx.guild.id and not event.is_cancelled
            and event.start_time > datetime.utcnow()
        ]
        
        if not guild_events:
            embed = discord.Embed(
                title="📅 No Upcoming Events",
                description="No events are currently scheduled for this server.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="💡 Create an Event",
                value="Use `?createevent` or `/createevent` to create a new event!",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Sort events by start time
        guild_events.sort(key=lambda x: x.start_time)
        
        embed = discord.Embed(
            title=f"📅 Upcoming Events ({len(guild_events)})",
            color=discord.Color.blue()
        )
        
        for event in guild_events[:10]:  # Show up to 10 events
            time_until = event.start_time - datetime.utcnow()
            days = time_until.days
            hours, remainder = divmod(time_until.seconds, 3600)
            
            time_text = f"In {days}d {hours}h" if days > 0 else f"In {hours}h {remainder//60}m"
            
            embed.add_field(
                name=f"🎯 {event.title}",
                value=f"**ID:** `{event.event_id}`\n"
                      f"**Time:** {event.start_time.strftime('%m/%d %H:%M')}\n"
                      f"**Status:** {time_text}\n"
                      f"**Attending:** {len(event.participants)}",
                inline=True
            )
        
        if len(guild_events) > 10:
            embed.set_footer(text=f"Showing first 10 of {len(guild_events)} events")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="eventinfo", description="Get detailed information about an event")
    @app_commands.describe(event_id="The ID of the event to view")
    async def event_info(self, ctx: commands.Context, event_id: str):
        """Get detailed information about a specific event."""
        event = self.events.get(event_id)
        
        if not event:
            embed = discord.Embed(
                title="❌ Event Not Found",
                description=f"No event found with ID `{event_id}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if event.guild_id != ctx.guild.id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You can only view events from this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = await self.create_event_embed(event)
        view = EventView(event, self.bot)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="cancelevent", description="Cancel an event")
    @app_commands.describe(event_id="The ID of the event to cancel")
    async def cancel_event(self, ctx: commands.Context, event_id: str):
        """Cancel an event (only creator or admin can cancel)."""
        event = self.events.get(event_id)
        
        if not event:
            embed = discord.Embed(
                title="❌ Event Not Found",
                description=f"No event found with ID `{event_id}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if event.guild_id != ctx.guild.id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You can only cancel events from this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Check permissions
        is_creator = ctx.author.id == event.creator_id
        is_admin = ctx.author.guild_permissions.administrator
        
        if not (is_creator or is_admin):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only the event creator or server administrators can cancel events.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if event.is_cancelled:
            embed = discord.Embed(
                title="ℹ️ Already Cancelled",
                description="This event is already cancelled.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        # Cancel event
        event.is_cancelled = True
        
        # Cancel Discord native event if it exists
        discord_cancelled = False
        if event.discord_event_id:
            try:
                discord_event = ctx.guild.get_scheduled_event(event.discord_event_id)
                if discord_event and discord_event.status != discord.EventStatus.cancelled:
                    await discord_event.cancel()
                    discord_cancelled = True
                    logger.info(f"Cancelled Discord event: {event.discord_event_id}")
            except Exception as e:
                logger.error(f"Error cancelling Discord event {event.discord_event_id}: {e}")
        
        await self.save_events()
        
        embed = discord.Embed(
            title="✅ Event Cancelled",
            description=f"Event `{event.title}` has been cancelled.",
            color=discord.Color.green()
        )
        
        if discord_cancelled:
            embed.add_field(
                name="🌐 Discord Event",
                value="✅ Also cancelled in server events",
                inline=False
            )
        elif event.discord_event_id:
            embed.add_field(
                name="🌐 Discord Event",
                value="⚠️ Could not cancel Discord event (may need manual cancellation)",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
        logger.info(f"Event cancelled: {event_id} by {ctx.author}")
    
    @tasks.loop(minutes=5)
    async def check_reminders(self):
        """Check for events that need reminders."""
        now = datetime.utcnow()
        
        for event in self.events.values():
            if (not event.is_cancelled and not event.reminder_sent and 
                event.start_time > now):
                
                # Send reminder 30 minutes before event
                time_until = event.start_time - now
                if time_until.total_seconds() <= 1800:  # 30 minutes
                    await self.send_event_reminder(event)
                    event.reminder_sent = True
                    await self.save_events()
    
    async def send_event_reminder(self, event: EventData):
        """Send reminder for an upcoming event."""
        try:
            channel = self.bot.get_channel(event.channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="⏰ Event Reminder",
                description=f"**{event.title}** is starting soon!",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="🕒 Start Time",
                value=event.start_time.strftime('%Y-%m-%d at %H:%M UTC'),
                inline=True
            )
            
            embed.add_field(
                name="👥 Attending",
                value=f"{len(event.participants)} people",
                inline=True
            )
            
            # Mention participants
            if event.participants:
                mentions = [f"<@{user_id}>" for user_id in event.participants[:10]]
                if len(event.participants) > 10:
                    mentions.append(f"and {len(event.participants) - 10} others")
                
                embed.add_field(
                    name="📢 Reminder for",
                    value=" ".join(mentions),
                    inline=False
                )
            
            await channel.send(embed=embed)
            logger.info(f"Sent reminder for event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error sending reminder for event {event.event_id}: {e}")
    
    @commands.hybrid_command(name="eventperms", description="Check bot permissions for creating Discord events")
    async def check_event_permissions(self, ctx: commands.Context):
        """Check if the bot has permissions to create Discord server events."""
        embed = discord.Embed(
            title="🔧 Bot Event Permissions Check",
            color=discord.Color.blue()
        )
        
        # Check Manage Events permission
        has_manage_events = ctx.guild.me.guild_permissions.manage_events
        
        embed.add_field(
            name="📅 Manage Events Permission",
            value="✅ Enabled" if has_manage_events else "❌ Missing",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot Status",
            value="✅ Ready to create Discord events" if has_manage_events else "⚠️ Cannot create Discord events",
            inline=True
        )
        
        if not has_manage_events:
            embed.add_field(
                name="🛠️ How to Fix",
                value="1. Go to **Server Settings** → **Roles**\n"
                      "2. Find the bot's role\n"
                      "3. Enable **Manage Events** permission\n"
                      "4. Save changes and try again",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Current Limitation",
                value="Bot events will still work, but won't appear in Discord's native Events tab",
                inline=False
            )
        else:
            embed.add_field(
                name="🎉 All Set!",
                value="The bot can create Discord server events that will appear in the Events tab",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        """Wait for bot to be ready before starting reminder checker."""
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    await bot.add_cog(EventsCog(bot))
