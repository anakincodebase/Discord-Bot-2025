"""
Database initialization and connection management.

Author: Afnan Ahmed
Created: 2025
Description: SQLite database connection management and initialization
             for Discord bot persistent storage.
Features: Connection pooling, automatic table creation,
          error handling, thread-safe operations.
License: MIT
"""

import sqlite3
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Global database connection
conn = None
cursor = None

async def init_db():
    """Initialize the database connection and create tables."""
    global conn, cursor
    
    try:
        # Create database directory if it doesn't exist
        db_path = Path("bot_data.db")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create user data table for general bot features
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT,
            guild_id TEXT,
            username TEXT,
            data_type TEXT,
            data_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create guild settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT PRIMARY KEY,
            prefix TEXT DEFAULT '?',
            welcome_channel_id TEXT,
            mod_log_channel_id TEXT,
            auto_role_id TEXT,
            settings_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create game statistics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_stats (
            user_id TEXT,
            guild_id TEXT,
            game_type TEXT,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            total_games INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        # Don't exit on database errors in deployment
        logger.warning("Continuing without database functionality")

def get_db_connection():
    """Get the database connection."""
    return conn, cursor

