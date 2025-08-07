# 🌙 Nightzone Discord Bot

A comprehensive Discord bot with music, moderation, fun commands, and AI chat capabilities.

## ✨ Features

- 🎵 **Music Player**: Play music from YouTube and Spotify with queue management
- 🛡️ **Moderation**: Advanced moderation tools for server management
- 🎮 **Games**: Hangman, Tic-Tac-Toe, Trivia, and more
- 🤖 **AI Chat**: Intelligent conversation with custom personality
- 📊 **Utilities**: User info, definitions, polls, and helpful commands
- 💬 **Fun Commands**: Ship calculator, avatar display, and social interactions

## 🏗️ Project Structure

```
discord-bot/
│
├── bot/                        # Main bot package
│   ├── __init__.py
│   ├── main.py                 # Entry point for the bot
│   ├── config.py               # Bot configuration settings
│   ├── cogs/                   # Organized command modules
│   │   ├── __init__.py
│   │   ├── music.py           # Music commands and controls
│   │   ├── fun.py             # Games and entertainment
│   │   ├── moderation.py      # Server moderation tools
│   │   └── utils.py           # Utility and misc commands
│   ├── database/               # Database management
│   │   ├── __init__.py
│   │   ├── db.py              # Database connection
│   │   └── models.py          # Data models and operations
│   └── helpers/                # Shared helper functions
│       ├── __init__.py
│       ├── checks.py          # Permission and rate limit checks
│       ├── hangman_game.py    # Hangman game logic
│       ├── trivia_data.py     # Trivia questions database
│       └── llm_chat.py        # AI chat functionality
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_commands.py       # Command tests
│
├── bin/                        # Binary files
│   └── ffmpeg/                # FFmpeg for audio processing
│
├── models/                     # AI model files
│   └── *.gguf                 # LLM model files
│
├── .env                        # Environment variables (create this)
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── song_queue.db             # SQLite database (auto-created)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (included in `bin/ffmpeg/`)
- Discord Bot Token
- Spotify API credentials (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd discord-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   OWNER_IDS=your_user_id,another_owner_id
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   WELCOME_CHANNEL_ID=1314698176833392651
   ```

4. **Run the bot**
   ```bash
   python -m bot.main
   ```

## 🎵 Music Commands

| Command | Description |
|---------|-------------|
| `?join` | Join your voice channel |
| `?leave` | Leave the voice channel |
| `?play <song>` | Play a song or playlist |
| `/play <song>` | Play command (slash version) |
| `?skip` | Skip current song |
| `?queue` | View the music queue |
| `?clearqueue` | Clear the entire queue |

### Music Controls
The bot provides interactive buttons for:
- ⏸️ Pause/Resume
- ⏭️ Skip
- 🔁 Repeat toggle
- 🔀 Shuffle queue
- 🗑️ Clear queue
- 🔊🔉 Volume control

## 🎮 Games & Fun

| Command | Description |
|---------|-------------|
| `?hangman` | Start a word guessing game |
| `?tictactoe @user` | Challenge someone to Tic-Tac-Toe |
| `?trivia` | Random trivia questions |
| `?ship @user1 @user2` | Love compatibility calculator |

## 🛡️ Moderation

| Command | Description | Required Role |
|---------|-------------|---------------|
| `?mute @user` | Mute a user | Staff/Admin |
| `?unmute @user` | Unmute a user | Staff/Admin |
| `?ban @user` | Ban a user | Staff/Admin |
| `?kick @user` | Kick a user | Staff/Admin |
| `?purge <amount>` | Delete messages | Staff/Admin |

## 🔧 Utility Commands

| Command | Description |
|---------|-------------|
| `?whois @user` | Detailed user information |
| `?avatar @user` | Display user's avatar |
| `?def <word>` | Get word definition |
| `?ask <message>` | Chat with AI assistant |
| `?help` | Show all commands |

## ⚙️ Configuration

### Environment Variables

- `DISCORD_TOKEN`: Your Discord bot token
- `OWNER_IDS`: Comma-separated list of bot owner user IDs
- `SPOTIFY_CLIENT_ID`: Spotify API client ID (optional)
- `SPOTIFY_CLIENT_SECRET`: Spotify API client secret (optional)
- `WELCOME_CHANNEL_ID`: Channel ID for welcome messages

### Permissions

The bot requires the following Discord permissions:
- Send Messages
- Use Slash Commands
- Connect to Voice Channels
- Speak in Voice Channels
- Manage Messages (for moderation)
- Manage Roles (for muting)

## 🤖 AI Chat Features

The bot includes an AI assistant with:
- Contextual conversation memory
- Custom personality (Nightzone)
- Emoji support and text formatting
- Rate limiting and spam protection

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Commands

1. Create or modify cogs in `bot/cogs/`
2. Register the cog in `bot/main.py`
3. Add tests in `tests/`

### Database Operations

The bot uses SQLite for queue management. Database operations are handled in `bot/database/models.py`.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🛠️ Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Check that the bot has proper permissions
   - Verify the token in `.env` file
   - Check console for error messages

2. **Music not playing**
   - Ensure FFmpeg is in the `bin/ffmpeg/` directory
   - Check voice channel permissions
   - Verify YouTube-DL is up to date

3. **AI chat not working**
   - Check if the LLM model file exists in `models/`
   - Verify model path in configuration
   - Check console for model loading errors

### Support

For support and questions, create an issue in the repository or contact the development team.

---

**Created by anakincodebase** 🌟
