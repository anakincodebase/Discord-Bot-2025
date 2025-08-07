# 🚀 UnderLand Bot - Deployment Guide

## 📋 Quick Start

### 1. Local Testing
```bash
# Install dependencies
pip install -r requirements_deployment.txt

# Set your bot token
export DISCORD_TOKEN="your_token_here"

# Run the bot
python run_deployment.py
```

### 2. Cloud Deployment Options

#### Option A: Railway (Recommended)
1. Fork this repository
2. Go to [Railway.app](https://railway.app)
3. Click "Deploy from GitHub repo"
4. Select your forked repository
5. Add environment variable: `DISCORD_TOKEN`
6. Deploy automatically!

#### Option B: Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create new app
heroku create your-bot-name

# Set environment variables
heroku config:set DISCORD_TOKEN="your_token_here"

# Deploy
git push heroku main
```

#### Option C: Render
1. Fork this repository
2. Go to [Render.com](https://render.com)
3. Create new "Web Service"
4. Connect your GitHub repository
5. Set environment variable: `DISCORD_TOKEN`
6. Deploy!

#### Option D: GitHub Actions (Continuous Deployment)
1. Fork this repository
2. Go to repository Settings > Secrets
3. Add secret: `DISCORD_TOKEN`
4. Push to main branch
5. Check Actions tab for deployment status

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | Your Discord bot token |
| `ENVIRONMENT` | ❌ No | Set to "production" for deployment |
| `OWNER_IDS` | ❌ No | Comma-separated user IDs for bot owners |
| `WELCOME_CHANNEL_ID` | ❌ No | Channel ID for welcome messages |

## 🎯 Features Included

### ✅ Deployment-Ready Features
- 🎮 Interactive Games (Hangman, Trivia, TicTacToe)
- 😄 Social Commands (Bonk, Hug, Kiss, Slap, etc.)
- 📚 Dictionary & Learning Tools
- ⏱️ Productivity Features (Pomodoro Timer)
- 🛠️ Moderation Tools (Mute, Kick, Ban, Purge)
- 🌐 Utility Commands (Ping, Status, Help)
- 🎭 Script Sessions

### ❌ Excluded for Cloud Deployment
- 🎵 Music commands (require ffmpeg)
- 🤖 AI chat features (require large models)
- 📁 Local file dependencies

## 📊 Performance Optimizations

- **Lightweight**: Only essential dependencies
- **Fast Startup**: Optimized initialization
- **Memory Efficient**: Minimal resource usage
- **Error Resilient**: Comprehensive error handling
- **24/7 Ready**: Designed for continuous operation

## 🛠️ Troubleshooting

### Common Issues

1. **Bot doesn't start**
   - Check if `DISCORD_TOKEN` is set correctly
   - Verify token has proper permissions

2. **Commands not working**
   - Ensure bot has message content intent enabled
   - Check bot permissions in Discord server

3. **Deployment fails**
   - Verify all required files are present
   - Check platform-specific configuration files

### Support Commands
- `?ping` - Check bot status and latency
- `?status` - Detailed bot information
- `?help` - Comprehensive help system

## 📝 File Structure

```
├── run_deployment.py              # Main deployment script
├── requirements_deployment.txt    # Lightweight dependencies
├── Procfile                      # Heroku configuration
├── railway.json                  # Railway configuration  
├── render.yaml                   # Render configuration
├── .github/workflows/deploy.yml  # GitHub Actions
├── bot/
│   ├── main_deployment.py        # Optimized bot core
│   ├── config_deployment.py      # Deployment config
│   └── cogs/                     # Feature modules
└── README_DEPLOYMENT.md          # This documentation
```

## 🔒 Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for sensitive data
3. **Set appropriate bot permissions** in Discord
4. **Enable 2FA** on your Discord account
5. **Regularly rotate tokens** if compromised

## 📈 Monitoring

### Health Checks
- The bot automatically sets status to show server count
- Use `?ping` to check responsiveness
- Monitor logs for error patterns

### Uptime Monitoring
- Most cloud platforms provide uptime monitoring
- Set up alerts for downtime
- Use external monitoring services if needed

## 🎯 Next Steps

1. **Deploy the bot** using your preferred platform
2. **Invite to servers** with appropriate permissions
3. **Test core features** using `?help`
4. **Monitor performance** and logs
5. **Customize settings** via environment variables

---

**Happy Deploying! 🚀**

Need help? Check the comprehensive help system with `?help` or review the troubleshooting section above.
