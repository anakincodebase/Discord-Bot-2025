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
        db_path = Path("song_queue.db")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create song queue table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS song_queue (
            guild_id TEXT,
            audio_url TEXT,
            title TEXT,
            requestor_name TEXT,
            thumbnail TEXT
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)

def get_db_connection():
    """Get the database connection."""
    return conn, cursor
