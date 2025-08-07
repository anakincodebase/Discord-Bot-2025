"""
Deployment Configuration Settings
Optimized configuration for cloud deployment without AI/Music dependencies.

Author: Afnan Ahmed
Created: 2025
Description: Lightweight configuration for 24/7 cloud deployment,
             excluding resource-intensive features like AI models and music.
License: MIT
"""

import os
from typing import List

class DeploymentConfig:
    """Lightweight configuration class for cloud deployment."""
    
    def __init__(self):
        # Essential bot configuration
        self.TOKEN = os.getenv("DISCORD_TOKEN")
        self.OWNER_IDS = self._parse_owner_ids(os.getenv("OWNER_IDS", ""))
        
        # Optional channel configuration
        self.WELCOME_CHANNEL_ID = self._safe_int_parse(
            os.getenv("WELCOME_CHANNEL_ID"), 
            None
        )
        
        # Rate limiting configuration
        self.RATE_LIMIT = 5
        self.TIME_WINDOW = 120  # seconds
        
        # Session timeouts
        self.CONVERSATION_TIMEOUT = 300  # 5 minutes
        self.GAME_TIMEOUT = 600  # 10 minutes
        
        # Deployment settings
        self.MAX_MESSAGE_LENGTH = 2000
        self.MAX_EMBED_FIELDS = 25
        self.COMMAND_COOLDOWN = 3  # seconds
        
    def _parse_owner_ids(self, owner_ids_str: str) -> List[str]:
        """Parse comma-separated owner IDs safely."""
        if not owner_ids_str:
            return []
        return [id.strip() for id in owner_ids_str.split(",") if id.strip().isdigit()]
    
    def _safe_int_parse(self, value: str, default=None) -> int:
        """Safely parse integer values with fallback."""
        if not value:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    @property
    def log_level(self) -> str:
        """Get appropriate log level for environment."""
        return "INFO" if self.is_production else "DEBUG"
