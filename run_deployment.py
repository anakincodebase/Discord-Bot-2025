#!/usr/bin/env python3
"""
UnderLand Discord Bot - Cloud Deployment Runner
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

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import the deployment-optimized bot
from bot.main_deployment import main

if __name__ == "__main__":
    # Ensure we're using the deployment configuration
    os.environ.setdefault("ENVIRONMENT", "production")
    
    # Validate required environment variables
    required_vars = ["DISCORD_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before deployment.")
        sys.exit(1)
    
    print("🚀 Starting UnderLand Bot - Cloud Deployment...")
    print("📊 Deployment Mode: Production")
    print("⚡ Features: Games, Social, Utilities, Moderation")
    print("🎯 Status: Optimized for 24/7 cloud hosting")
    
    # Run the bot
    import asyncio
    asyncio.run(main())
