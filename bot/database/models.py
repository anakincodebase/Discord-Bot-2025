"""
Database models and operations for Discord bot data management.

Author: Afnan Ahmed
Created: 2025
Description: Comprehensive data management system for Discord bot
             with SQLite persistence for user data, guild settings, and game statistics.
License: MIT
"""

import sqlite3
import logging
import json
from typing import Dict, Optional, Any
from datetime import datetime

from .db import get_db_connection

logger = logging.getLogger(__name__)

# In-memory cache for frequently accessed data
GUILD_SETTINGS_CACHE = {}
USER_DATA_CACHE = {}

def get_guild_settings(guild_id: str) -> Dict[str, Any]:
    """Get guild settings from database or cache."""
    try:
        # Check cache first
        if guild_id in GUILD_SETTINGS_CACHE:
            return GUILD_SETTINGS_CACHE[guild_id]
        
        conn, cursor = get_db_connection()
        if not conn:
            return get_default_guild_settings()
            
        cursor.execute('''
        SELECT prefix, welcome_channel_id, mod_log_channel_id, auto_role_id, settings_json
        FROM guild_settings WHERE guild_id = ?
        ''', (guild_id,))
        
        result = cursor.fetchone()
        if result:
            settings = {
                'prefix': result[0] or '?',
                'welcome_channel_id': result[1],
                'mod_log_channel_id': result[2],
                'auto_role_id': result[3],
                'custom_settings': json.loads(result[4] or '{}')
            }
        else:
            # Insert default settings
            settings = get_default_guild_settings()
            set_guild_settings(guild_id, settings)
        
        # Cache the settings
        GUILD_SETTINGS_CACHE[guild_id] = settings
        return settings
        
    except (sqlite3.Error, json.JSONDecodeError) as e:
        logger.error(f"Failed to get guild settings for {guild_id}: {e}")
        return get_default_guild_settings()

def set_guild_settings(guild_id: str, settings: Dict[str, Any]) -> bool:
    """Update guild settings in database."""
    try:
        conn, cursor = get_db_connection()
        if not conn:
            return False
            
        cursor.execute('''
        INSERT OR REPLACE INTO guild_settings 
        (guild_id, prefix, welcome_channel_id, mod_log_channel_id, auto_role_id, settings_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            guild_id,
            settings.get('prefix', '?'),
            settings.get('welcome_channel_id'),
            settings.get('mod_log_channel_id'),
            settings.get('auto_role_id'),
            json.dumps(settings.get('custom_settings', {})),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        
        # Update cache
        GUILD_SETTINGS_CACHE[guild_id] = settings
        
        logger.info(f"Updated guild settings for {guild_id}")
        return True
        
    except (sqlite3.Error, json.JSONDecodeError) as e:
        logger.error(f"Failed to set guild settings for {guild_id}: {e}")
        return False

def get_default_guild_settings() -> Dict[str, Any]:
    """Get default guild settings."""
    return {
        'prefix': '?',
        'welcome_channel_id': None,
        'mod_log_channel_id': None,
        'auto_role_id': None,
        'custom_settings': {}
    }

def get_user_data(user_id: str, guild_id: str, data_type: str) -> Optional[str]:
    """Get user data from database."""
    try:
        cache_key = f"{user_id}:{guild_id}:{data_type}"
        if cache_key in USER_DATA_CACHE:
            return USER_DATA_CACHE[cache_key]
            
        conn, cursor = get_db_connection()
        if not conn:
            return None
            
        cursor.execute('''
        SELECT data_value FROM user_data 
        WHERE user_id = ? AND guild_id = ? AND data_type = ?
        ORDER BY created_at DESC LIMIT 1
        ''', (user_id, guild_id, data_type))
        
        result = cursor.fetchone()
        value = result[0] if result else None
        
        # Cache the result
        USER_DATA_CACHE[cache_key] = value
        return value
        
    except sqlite3.Error as e:
        logger.error(f"Failed to get user data: {e}")
        return None

def set_user_data(user_id: str, guild_id: str, username: str, data_type: str, data_value: str) -> bool:
    """Set user data in database."""
    try:
        conn, cursor = get_db_connection()
        if not conn:
            return False
            
        cursor.execute('''
        INSERT INTO user_data (user_id, guild_id, username, data_type, data_value)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, guild_id, username, data_type, data_value))
        
        conn.commit()
        
        # Update cache
        cache_key = f"{user_id}:{guild_id}:{data_type}"
        USER_DATA_CACHE[cache_key] = data_value
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Failed to set user data: {e}")
        return False

def get_game_stats(user_id: str, guild_id: str, game_type: str) -> Dict[str, int]:
    """Get game statistics for a user."""
    try:
        conn, cursor = get_db_connection()
        if not conn:
            return {'wins': 0, 'losses': 0, 'total_games': 0}
            
        cursor.execute('''
        SELECT wins, losses, total_games FROM game_stats
        WHERE user_id = ? AND guild_id = ? AND game_type = ?
        ''', (user_id, guild_id, game_type))
        
        result = cursor.fetchone()
        if result:
            return {
                'wins': result[0],
                'losses': result[1], 
                'total_games': result[2]
            }
        else:
            return {'wins': 0, 'losses': 0, 'total_games': 0}
            
    except sqlite3.Error as e:
        logger.error(f"Failed to get game stats: {e}")
        return {'wins': 0, 'losses': 0, 'total_games': 0}

def update_game_stats(user_id: str, guild_id: str, game_type: str, won: bool) -> bool:
    """Update game statistics for a user."""
    try:
        conn, cursor = get_db_connection()
        if not conn:
            return False
            
        # Get current stats
        stats = get_game_stats(user_id, guild_id, game_type)
        
        # Update stats
        stats['total_games'] += 1
        if won:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        # Insert or update record
        cursor.execute('''
        INSERT OR REPLACE INTO game_stats 
        (user_id, guild_id, game_type, wins, losses, total_games, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, guild_id, game_type,
            stats['wins'], stats['losses'], stats['total_games'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Failed to update game stats: {e}")
        return False

def get_leaderboard(guild_id: str, game_type: str, limit: int = 10) -> list:
    """Get leaderboard for a specific game type."""
    try:
        conn, cursor = get_db_connection()
        if not conn:
            return []
            
        cursor.execute('''
        SELECT user_id, wins, losses, total_games
        FROM game_stats
        WHERE guild_id = ? AND game_type = ?
        ORDER BY wins DESC, total_games DESC
        LIMIT ?
        ''', (guild_id, game_type, limit))
        
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        logger.error(f"Failed to get leaderboard: {e}")
        return []

def clear_user_cache(user_id: str = None, guild_id: str = None):
    """Clear user data cache."""
    global USER_DATA_CACHE
    
    if user_id and guild_id:
        # Clear specific user's cache
        keys_to_remove = [key for key in USER_DATA_CACHE.keys() 
                         if key.startswith(f"{user_id}:{guild_id}:")]
        for key in keys_to_remove:
            del USER_DATA_CACHE[key]
    else:
        # Clear all cache
        USER_DATA_CACHE.clear()
    
    logger.info("User data cache cleared")

def clear_guild_cache(guild_id: str = None):
    """Clear guild settings cache."""
    global GUILD_SETTINGS_CACHE
    
    if guild_id:
        GUILD_SETTINGS_CACHE.pop(guild_id, None)
    else:
        GUILD_SETTINGS_CACHE.clear()
    
    logger.info("Guild settings cache cleared")


