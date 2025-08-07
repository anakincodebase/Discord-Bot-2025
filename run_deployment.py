#!/usr/bin/env python3
"""
Deploy UnderLand Bot - Cloud Deployment Runner
Professional deployment script for 24/7 hosting platforms.

Author: Afnan Ahmed
Created: 2025
Description: Production-ready deployment script optimized for cloud platforms
             like Heroku, Railway, Render, or GitHub Actions.
License: MIT
"""

import os
import sys
import logging
from pathlib import Path

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Setup deployment logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def validate_environment():
    """Validate required environment variables for deployment."""
    required_vars = ["DISCORD_TOKEN"]
    optional_vars = ["WELCOME_CHANNEL_ID", "OWNER_ID"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these environment variables before deployment.")
        return False
    
    # Log optional variables status
    for var in optional_vars:
        if os.getenv(var):
            logger.info(f"✅ Optional variable {var} is set")
        else:
            logger.warning(f"⚠️ Optional variable {var} is not set")
    
    return True

async def deploy_underland_bot():
    """Deploy the UnderLand Bot with proper error handling."""
    try:
        # Import the deployment-optimized bot
        from bot.main_deployment import main
        
        logger.info("🚀 Starting Deploy UnderLand Bot - Cloud Deployment...")
        logger.info("📊 Deployment Mode: Production")
        logger.info("⚡ Features: Games, Social, Utilities, Moderation")
        logger.info("🎯 Status: Optimized for 24/7 cloud hosting")
        
        # Run the bot
        await main()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import bot modules: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure we're using the deployment configuration
    os.environ.setdefault("ENVIRONMENT", "production")
    
    # Validate environment before starting
    if not validate_environment():
        sys.exit(1)
    
    # Deploy the bot
    import asyncio
    try:
        asyncio.run(deploy_underland_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Deployment interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Failed to start deployment: {e}")
        sys.exit(1)
