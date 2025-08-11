"""
Moderation commands for the Discord bot.
"""

import logging
from typing import Optional

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class ModerationCog(commands.Cog):
    """Moderation commands cog."""
    
    def __init__(self, bot):
        self.bot = bot

    def has_permission(self, user: discord.Member) -> bool:
        """Check if user has moderation permissions."""
        if user.guild_permissions.administrator:
            return True
        
        allowed_roles = ["Staff", "Admin", "FunnyCommands", "Parliamentarian"]
        user_roles = [role.name for role in user.roles]
        return any(role in user_roles for role in allowed_roles)

    def is_owner(self, user_id: str) -> bool:
        """Check if user is bot owner."""
        return user_id in self.bot.config.OWNER_IDS

    @commands.command(name="mute")
    @commands.has_any_role("Admin", "Staff", "Parliamentarian")
    async def mute(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Mute a user in the server."""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    mute_role, 
                    speak=False, 
                    send_messages=False, 
                    read_message_history=True, 
                    read_messages=False
                )

        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"Muted {member.mention} for reason: {reason}")

    @commands.command(name="unmute")
    @commands.has_any_role("Admin", "Staff", "Parliamentarian")
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a user in the server."""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"Unmuted {member.mention}")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.command(name="ban")
    @commands.has_any_role("Admin", "Staff", "Parliamentarian")
    async def ban(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Ban a user from the server."""
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Banned {member.mention} for reason: {reason}")
        except discord.Forbidden:
            logger.error(f"Failed to ban {member}. Insufficient permissions.")
            await ctx.send(f"Could not ban {member.mention}. I lack the necessary permissions.")
        except Exception as e:
            logger.error(f"Unexpected error while banning {member}: {e}")
            await ctx.send(f"An error occurred while trying to ban {member.mention}.")

    @commands.command(name="kick")
    @commands.has_any_role("Admin", "Staff", "Parliamentarian")
    async def kick(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Kick a user from the server."""
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Kicked {member.mention} for reason: {reason}")
        except discord.Forbidden:
            logger.error(f"Failed to kick {member}. Insufficient permissions.")
            await ctx.send(f"Could not kick {member.mention}. I lack the necessary permissions.")
        except Exception as e:
            logger.error(f"Unexpected error while kicking {member}: {e}")
            await ctx.send(f"An error occurred while trying to kick {member.mention}.")

    @commands.command(name="purge")
    @commands.has_any_role("Admin", "Staff", "Parliamentarian", "Funnycommands")
    async def purge(self, ctx, limit: int):
        """Delete multiple messages at once."""
        try:
            if not self.is_owner(str(ctx.author.id)) and not self.has_permission(ctx.author):
                await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
                return

            if limit < 1:
                await ctx.send("Please specify a positive number of messages to delete.")
                return

            deleted = await ctx.channel.purge(limit=limit)
            await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)

        except commands.MissingAnyRole as e:
            await ctx.send(f"Error: {e}. You are missing the required roles to use this command.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to delete messages in this channel.")
        except discord.HTTPException as e:
            await ctx.send(f"An HTTP error occurred: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")

    @commands.command(name="dm")
    @commands.has_any_role("Admin", "Staff", "Parliamentarian")
    async def dm(self, ctx, user: discord.User, *, message: str):
        """Send a direct message to a user."""
        if not self.is_owner(str(ctx.author.id)) and not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return

        try:
            await user.send(message)
            await ctx.send(f"Sent a DM to {user.mention}.")
        except discord.Forbidden:
            logger.warning(f"Failed to send DM to {user}. User might have DMs disabled.")
            await ctx.send(f"Could not send a DM to {user.mention}. They might have DMs disabled.")
        except Exception as e:
            logger.error(f"Unexpected error while sending DM to {user}: {e}")
            await ctx.send(f"An error occurred while trying to send a DM to {user.mention}.")

    @commands.command(name="order66")
    async def order66(self, ctx):
        """Make the bot leave the server (owner only)."""
        if not self.is_owner(str(ctx.author.id)):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return

        await ctx.send("Executing Order 66... Goodbye!")
        await ctx.guild.leave()

    @commands.command(name="hardshutdown")
    async def hardshutdown(self, ctx):
        """Shutdown the bot (owner only)."""
        if not self.is_owner(str(ctx.author.id)):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command is restricted to bot owners only.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="🛑 Bot Shutdown",
            description="Bot is shutting down now...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Bot shutdown initiated by {ctx.author} ({ctx.author.id})")
        await self.bot.close()

    @commands.command(name="superhardshutdown")
    @commands.is_owner()
    async def superhardshutdown(self, ctx):
        """Send shutdown signal (owner only)."""
        with open('shutdown_signal', 'w') as f:
            f.write('shutdown')
        await ctx.send("Shutdown signal sent. Runner will stop.")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(ModerationCog(bot))
