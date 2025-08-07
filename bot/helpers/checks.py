"""
Helper functions for permission checks and other utilities.
"""

import time
from collections import defaultdict
from typing import List

import discord
from discord.ext import commands

# Rate limiting
user_command_timestamps = defaultdict(list)
RATE_LIMIT = 5
TIME_WINDOW = 120  # seconds

async def is_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited."""
    current_time = time.time()
    timestamps = user_command_timestamps[user_id]

    # Remove timestamps outside time window
    user_command_timestamps[user_id] = [
        timestamp for timestamp in timestamps 
        if current_time - timestamp < TIME_WINDOW
    ]

    # Check if user exceeded rate limit
    if len(user_command_timestamps[user_id]) >= RATE_LIMIT:
        return True

    # Add current timestamp
    user_command_timestamps[user_id].append(current_time)
    return False

def has_permission(user: discord.Member) -> bool:
    """Check if user has permission to use certain commands."""
    if user.guild_permissions.administrator:
        return True
    
    allowed_roles = ["Staff", "Admin", "FunnyCommands", "Parliamentarian"]
    user_roles = [role.name for role in user.roles]
    return any(role in user_roles for role in allowed_roles)

def is_owner(user_id: str, owner_ids: List[str]) -> bool:
    """Check if user is bot owner."""
    return user_id in owner_ids
