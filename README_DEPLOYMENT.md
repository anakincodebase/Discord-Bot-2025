![UnderLand National Flag](Underland_National_Flag.png)

# UnderLand Discord Bot - Cloud Deployment Edition

## 🌟 Professional Discord Bot for 24/7 Deployment

A lightweight, feature-rich Discord bot optimized for cloud deployment without resource-intensive dependencies like AI models or ffmpeg.

### ✨ Features

#### 🎮 Interactive Games

- **Hangman** - Word guessing game with multiple categories
- **Trivia** - Timed trivia questions with scoring
- **TicTacToe** - Challenge friends to classic gameplay
- **Ship Calculator** - Fun compatibility ratings

#### 😄 Social Commands

- **Bonk, Hug, Kiss, Slap** - Animated social interactions
- **Avatar Display** - Show user profile pictures
- **Reaction Commands** - Expressive emoji responses

#### 📚 Learning & Utilities

- **Dictionary** - Word definitions and associations
- **User Info** - Detailed user information display
- **Interactive Polls** - Create engaging server polls

#### ⏱️ Productivity

- **Pomodoro Timer** - Focus sessions with customizable intervals
- **Progress Tracking** - Monitor productivity sessions

#### 🛠️ Moderation

- **User Management** - Mute, kick, ban with reasons
- **Message Management** - Bulk message deletion
- **Permission Controls** - Role-based command access

#### 🎭 Interactive Features

- **Script Sessions** - Story-based roleplay experiences
- **Enhanced Help System** - Comprehensive command documentation

### 🚀 Deployment Ready

#### Cloud Platform Support

- ✅ **Heroku** - Procfile included
- ✅ **Railway** - Railway.json configuration
- ✅ **Render** - render.yaml ready
- ✅ **GitHub Actions** - Automated CI/CD
- ✅ **Replit** - Browser-based hosting

#### Optimizations

- 🔹 **Lightweight Dependencies** - No AI models or ffmpeg
- 🔹 **Fast Startup** - Optimized initialization
- 🔹 **Memory Efficient** - Minimal resource usage
- 🔹 **Error Resilient** - Comprehensive error handling
- 🔹 **24/7 Ready** - Designed for continuous operation

### 📋 Quick Setup

#### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd Discord-bot

# Install dependencies
pip install -r requirements_deployment.txt

# Set environment variables
export DISCORD_TOKEN="your_bot_token_here"

# Run the bot
python run_deployment.py
```

#### Environment Variables
```env
DISCORD_TOKEN=your_discord_bot_token
ENVIRONMENT=production
OWNER_IDS=your_user_id,another_user_id  # Optional
WELCOME_CHANNEL_ID=channel_id  # Optional
```

### 🎯 Commands Overview

#### Fun & Games
- `?hangman` - Start word guessing game
- `?trivia` - Random trivia questions
- `?tictactoe @user` - Challenge to TicTacToe
- `?ship @user1 @user2` - Love compatibility

#### Social Interaction
- `?bonk @user` - Playful bonk with reactions
- `?hug @user` - Warm hug with animations
- `?avatar @user` - Display user's avatar
- `?say <message>` - Make bot repeat message

#### Utilities
- `?def <word>` - Get word definition
- `?whois @user` - User information
- `?poll <question> <option1> <option2>` - Create poll
- `?ping` - Check bot latency

#### Productivity
- `?pomodoro [duration]` - Start focus session
- Status tracking and notifications

#### Moderation
- `?mute @user [reason]` - Temporarily mute user
- `?kick @user [reason]` - Kick user from server
- `?ban @user [reason]` - Ban user from server
- `?purge <amount>` - Delete messages in bulk

### 🏗️ Architecture

```
bot/
├── main_deployment.py          # Optimized main bot file
├── config_deployment.py        # Deployment configuration
├── cogs/
│   ├── fun.py                 # Games and entertainment
│   ├── moderation.py          # Server management
│   ├── utils.py               # Utility commands
│   ├── pomodoro.py            # Productivity features
│   ├── enhanced_help_deployment.py  # Help system
│   └── script_session.py     # Interactive features
├── database/
│   ├── db.py                  # Database connection
│   └── models.py              # Data models
└── helpers/
    └── various utility modules
```

### 🔧 Deployment Platforms

#### Heroku
```bash
# Create Procfile
echo "worker: python run_deployment.py" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### Railway
```bash
# Use railway.json configuration
railway up
```

#### Render
```bash
# Use render.yaml configuration
# Connect your GitHub repository
```

#### GitHub Actions
```bash
# Set repository secrets:
# DISCORD_TOKEN
# Push to main branch for auto-deployment
```

### 🎨 Professional Features

#### Error Handling
- Intelligent command suggestions for typos
- Graceful error recovery
- Comprehensive logging system
- User-friendly error messages

#### Performance
- Async/await optimization
- Memory-efficient operations
- Rate limiting protection
- Fast command response times

#### User Experience
- Interactive help system with dropdowns
- Rich embed responses
- Emoji reactions and animations
- Intuitive command structure

### 📊 Statistics

- **30+ Commands** across 7 categories
- **Multiple Prefixes** (`?`, `!`, `n!`, `nz!`)
- **Production Ready** with comprehensive error handling
- **Lightweight** with minimal dependencies
- **Scalable** architecture for growth

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### 📄 License

MIT License - Feel free to use and modify for your projects.

### 👨‍💻 Author

**Afnan Ahmed**


### 🆘 Support

For support and questions:
1. Check the comprehensive help system (`?help`)
2. Review the command documentation
3. Check GitHub issues for common problems

---


