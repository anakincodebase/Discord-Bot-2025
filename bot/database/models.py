"""
Database models and operations for song queue management.

Author: Afnan Ahmed
Created: 2025
Description: Comprehensive song queue management system for Discord music bot
             with SQLite persistence, repeat functionality, and state management.
License: MIT
"""

import sqlite3
import logging
from collections import deque
from typing import List, Optional, Tuple

from .db import get_db_connection

logger = logging.getLogger(__name__)

# Dictionary to store song queues for each guild
SONG_QUEUES = {}

# Dictionary to store repeat status for each guild
REPEAT_STATUS = {}

# Dictionary to store last messages for each guild
LAST_MESSAGES = {}

def add_song_to_queue(guild_id: str, audio_url: str, title: str, requestor_name: str, thumbnail: str) -> None:
    """Add a song to the queue."""
    logger.info(f"Adding song to queue: {title} by {requestor_name} in guild {guild_id}")
    
    try:
        conn, cursor = get_db_connection()
        
        # Add to in-memory queue
        if guild_id not in SONG_QUEUES:
            SONG_QUEUES[guild_id] = deque()
        SONG_QUEUES[guild_id].append((audio_url, title, requestor_name, thumbnail))
        
        # Add to database
        cursor.execute('''
        INSERT INTO song_queue (guild_id, audio_url, title, requestor_name, thumbnail)
        VALUES (?, ?, ?, ?, ?)
        ''', (guild_id, audio_url, title, requestor_name, thumbnail))
        conn.commit()
        
    except sqlite3.Error as e:
        logger.error(f"Failed to add song to queue: {e}")

def get_next_song_from_queue(guild_id: str) -> Optional[Tuple[str, str, str, str]]:
    """Get the next song from the queue."""
    logger.info(f"Getting next song from queue for guild {guild_id}")
    
    try:
        conn, cursor = get_db_connection()
        
        # Get from in-memory queue
        if guild_id in SONG_QUEUES and SONG_QUEUES[guild_id]:
            return SONG_QUEUES[guild_id].popleft()
        
        # Get from database
        cursor.execute('''
        SELECT audio_url, title, requestor_name, thumbnail
        FROM song_queue
        WHERE guild_id = ?
        ORDER BY rowid ASC
        LIMIT 1
        ''', (guild_id,))
        
        song = cursor.fetchone()
        if song:
            cursor.execute('''
            DELETE FROM song_queue
            WHERE guild_id = ? AND audio_url = ? AND title = ? AND requestor_name = ? AND thumbnail = ?
            ''', (guild_id, *song))
            conn.commit()
        
        return song
        
    except sqlite3.Error as e:
        logger.error(f"Failed to get next song from queue: {e}")
        return None

def clear_queue(guild_id: str) -> None:
    """Clear the queue for a guild."""
    logger.info(f"Clearing queue for guild {guild_id}")
    
    try:
        conn, cursor = get_db_connection()
        
        # Clear in-memory queue
        if guild_id in SONG_QUEUES:
            SONG_QUEUES[guild_id].clear()
            logger.info(f"In-memory queue cleared for guild {guild_id}")
        
        # Clear database
        cursor.execute('DELETE FROM song_queue WHERE guild_id = ?', (guild_id,))
        conn.commit()
        logger.info(f"Database queue cleared for guild {guild_id}")
        
    except sqlite3.Error as e:
        logger.error(f"Failed to clear queue for guild {guild_id}: {e}")

def advanced_clear_queue(guild_id: str) -> None:
    """Advanced queue clearing with state reset."""
    logger.info(f"Advanced clearing queue for guild {guild_id}")
    
    try:
        # Clear queue
        clear_queue(guild_id)
        
        # Reset repeat status to prevent unwanted looping
        if guild_id in REPEAT_STATUS:
            REPEAT_STATUS[guild_id] = False
            logger.info(f"Repeat status disabled for guild {guild_id}")
            
        if guild_id in LAST_MESSAGES:
            LAST_MESSAGES.pop(guild_id)
            logger.info(f"Last messages reset for guild {guild_id}")
            
    except Exception as e:
        logger.error(f"Failed to advanced clear queue for guild {guild_id}: {e}")

def get_queue(guild_id: str) -> List[Tuple]:
    """Get the current queue for a guild."""
    logger.info(f"Getting queue for guild {guild_id}")
    
    try:
        conn, cursor = get_db_connection()
        
        # Get from in-memory queue
        if guild_id in SONG_QUEUES:
            return list(SONG_QUEUES[guild_id])
        
        # Get from database
        cursor.execute('''
        SELECT audio_url, title, requestor_name, thumbnail
        FROM song_queue
        WHERE guild_id = ?
        ORDER BY rowid ASC
        ''', (guild_id,))
        
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        logger.error(f"Failed to get queue: {e}")
        return []

def remove_song_from_queue(guild_id: str, title: str) -> None:
    """Remove a specific song from the queue."""
    logger.info(f"Removing song {title} from queue for guild {guild_id}")
    
    try:
        conn, cursor = get_db_connection()
        
        # Remove from in-memory queue
        if guild_id in SONG_QUEUES:
            SONG_QUEUES[guild_id] = deque(
                song for song in SONG_QUEUES[guild_id] if song[1] != title
            )
        
        # Remove from database
        cursor.execute('''
        DELETE FROM song_queue
        WHERE guild_id = ? AND title = ?
        ''', (guild_id, title))
        conn.commit()
        
    except sqlite3.Error as e:
        logger.error(f"Failed to remove song from queue: {e}")

def list_all_songs(guild_id: str) -> List[Tuple]:
    """List all songs in the queue."""
    logger.info(f"Listing all songs in queue for guild {guild_id}")
    
    try:
        conn, cursor = get_db_connection()
        
        # List from in-memory queue
        if guild_id in SONG_QUEUES:
            return list(SONG_QUEUES[guild_id])
        
        # List from database
        cursor.execute('''
        SELECT audio_url, title, requestor_name, thumbnail
        FROM song_queue
        WHERE guild_id = ?
        ORDER BY rowid ASC
        ''', (guild_id,))
        
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        logger.error(f"Failed to list all songs: {e}")
        return []

def pop_next_song(guild_id: str) -> Optional[Tuple[str, str, str, str]]:
    """Remove and return the next song from the queue."""
    logger.info(f"Popping next song from queue for guild {guild_id}")
    return get_next_song_from_queue(guild_id)

def get_queue_length(guild_id: str) -> int:
    """Get the number of songs in the queue."""
    if guild_id in SONG_QUEUES:
        return len(SONG_QUEUES[guild_id])
    
    try:
        conn, cursor = get_db_connection()
        cursor.execute('SELECT COUNT(*) FROM song_queue WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"Failed to get queue length: {e}")
        return 0

def is_repeat_enabled(guild_id: str) -> bool:
    """Check if repeat is enabled for a guild."""
    # Default to False to prevent unwanted repeating
    return REPEAT_STATUS.get(guild_id, False)

def set_repeat_status(guild_id: str, status: bool) -> None:
    """Set repeat status for a guild."""
    REPEAT_STATUS[guild_id] = status
    logger.info(f"Set repeat status to {status} for guild {guild_id}")

def ensure_clean_state(guild_id: str) -> None:
    """Ensure clean state for a guild - no unwanted repeat loops."""
    # Default repeat to False for clean playback
    if guild_id not in REPEAT_STATUS:
        REPEAT_STATUS[guild_id] = False
        logger.info(f"Initialized clean state (repeat=False) for guild {guild_id}")

def get_queue_info(guild_id: str) -> dict:
    """Get comprehensive queue information."""
    queue = get_queue(guild_id)
    return {
        "queue_length": len(queue),
        "songs": queue,
        "repeat_enabled": is_repeat_enabled(guild_id),
        "current_song": queue[0] if queue else None
    }
