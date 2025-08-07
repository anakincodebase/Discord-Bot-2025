# 🏰 UnderLand Discord Bot - Cloud Deployment Edition


A lightweight, professional Discord bot optimized for 24/7 cloud deployment. Features games, social commands, utilities, and moderation tools without heavy dependencies.

## ✨ Features Available

### 🎮 Games & Entertainment
- **Hangman** (`?hangman`) - Classic word guessing game
- **Trivia** (`?trivia`) - Random knowledge questions  
- **TicTacToe** (`?tictactoe @user`) - Challenge users to TicTacToe
- **Ship Calculator** (`?ship @user1 @user2`) - Fun compatibility ratings

### 😄 Social Commands
- **Bonk** (`?bonk @user`) - Playful bonk with reactions
- **Hug** (`?hug @user`) - Warm hug interactions
- **Kiss** (`?kiss @user`) - Sweet kiss commands
- **Slap** (`?slap @user`) - Playful slap interactions
- **Avatar** (`?avatar @user`) - Display user profile pictures

### 📚 Utilities
- **Dictionary** (`?def <word>`) - Word definitions and meanings
- **User Info** (`?whois @user`) - Detailed user information
- **Polls** (`?poll <question> <option1> <option2>`) - Interactive polls
- **Ping** (`?ping`) - Check bot latency and status
- **Say** (`?say <message>`) - Make bot repeat messages

### ⏱️ Productivity
- **Pomodoro Timer** (`?pomodoro [minutes]`) - Focus sessions with notifications
- **Status Tracking** - Monitor productivity sessions

### 🛠️ Moderation
- **Mute** (`?mute @user [reason]`) - Temporarily mute users
- **Kick** (`?kick @user [reason]`) - Remove users from server
- **Ban** (`?ban @user [reason]`) - Permanently ban users
- **Purge** (`?purge <amount>`) - Bulk delete messages

### 🎭 Interactive
- **Script Sessions** (`?script`) - Story-based roleplay experiences
- **Enhanced Help** (`?help`) - Comprehensive command documentation with dropdowns

## 🚀 Quick Deployment Guide

### Step 1: Repository Setup
```bash
# Clone or download this repository
git clone <your-repo-url>
cd Discord-bot
```

### Step 2: GitHub Secrets Configuration
Add these secrets in your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add **New repository secret**:

**Required:**
- `DISCORD_TOKEN` - Your Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

**Optional:**
- `OWNER_IDS` - Comma-separated Discord user IDs (e.g., `123456789,987654321`)
- `WELCOME_CHANNEL_ID` - Discord channel ID for welcome messages

### Step 3: Deploy
Simply push to the `main` branch and GitHub Actions will automatically deploy your bot!

```bash
git add .
git commit -m "Deploy UnderLand Bot"
git push origin main
```

## 🎯 Command Prefixes

The bot responds to multiple prefixes:
- `?` (primary)
- `!`
- `n!`
- `nz!`

## 📋 Available Commands List

```
🎮 GAMES & FUN
?hangman                    - Start word guessing game
?trivia                     - Random trivia questions
?tictactoe @user           - Challenge to TicTacToe
?ship @user1 @user2        - Love compatibility test

😄 SOCIAL
?bonk @user                - Playful bonk interaction
?hug @user                 - Warm hug with animations
?kiss @user                - Sweet kiss command
?slap @user                - Playful slap interaction
?avatar [@user]            - Show profile picture

📚 UTILITIES
?def <word>                - Get word definition
?whois [@user]             - User information display
?poll <question> <opt1> <opt2> - Create interactive poll
?ping                      - Check bot status & latency
?say <message>             - Make bot repeat message

⏱️ PRODUCTIVITY
?pomodoro [minutes]        - Start focus timer session

🛠️ MODERATION (Admin Only)
?mute @user [reason]       - Mute user temporarily
?kick @user [reason]       - Kick user from server
?ban @user [reason]        - Ban user permanently
?purge <amount>            - Delete multiple messages

🎭 INTERACTIVE
?script                    - Start roleplay session
?help                      - Comprehensive help system
```

## 🏗️ Project Structure

```
Discord-bot/
├── bot/
│   ├── main_deployment.py           # Main bot file
│   ├── config_deployment.py         # Configuration
│   └── cogs/
│       ├── fun.py                   # Games & entertainment
│       ├── moderation.py            # Server management
│       ├── utils.py                 # Utility commands
│       ├── pomodoro.py              # Productivity timer
│       ├── enhanced_help_deployment.py # Help system
│       └── script_session.py       # Interactive features
├── requirements_deployment.txt       # Dependencies
├── run_deployment.py                # Startup script
├── .github/workflows/deploy.yml     # Auto-deployment
└── README.md                        # This file
```

## 🔧 Cloud Platform Support

- ✅ **GitHub Actions** - Automated deployment (included)
- ✅ **Heroku** - Procfile ready
- ✅ **Railway** - Configuration included
- ✅ **Render** - YAML configuration ready
- ✅ **Replit** - Browser-based hosting

## 📊 Technical Specifications

- **Commands**: 20+ interactive commands
- **Prefixes**: 4 different command prefixes
- **Dependencies**: Only 6 lightweight packages
- **Memory Usage**: < 100MB RAM
- **Startup Time**: 3-5 seconds
- **Uptime**: Designed for 24/7 operation

## 🛡️ Key Features

- **Error Handling** - Comprehensive error recovery
- **Rate Limiting** - Built-in spam protection  
- **Async Operations** - Optimized performance
- **Rich Embeds** - Beautiful command responses
- **Interactive Help** - Dropdown menu navigation
- **Logging System** - Production-ready monitoring

## 🎨 Professional Quality

- Clean, organized codebase
- Comprehensive error handling
- Production-ready deployment
- Professional documentation
- Scalable architecture
- Memory optimized

## 📄 License

MIT License - Free to use and modify for your projects.

## 👨‍💻 Author

**Afnan Ahmed**

## 🆘 Support

For help and questions:
1. Use `?help` command in Discord
2. Check GitHub Actions logs for deployment issues
3. Ensure Discord bot permissions are correct

---


**Ready to deploy! 🚀** Just add your `DISCORD_TOKEN` to GitHub secrets and push to main branch.
