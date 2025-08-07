# 🔑 GitHub Secrets Configuration Guide

## Required Secrets for GitHub Actions Deployment

To deploy your UnderLand Bot using GitHub Actions, you need to configure the following secrets in your repository.

### 📋 How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret below

### 🔒 Required Secrets

#### `DISCORD_TOKEN` (Required)
- **Description**: Your Discord bot token
- **How to get it**:
  1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
  2. Select your bot application
  3. Go to **Bot** section
  4. Copy the token under **Token** section
- **Example**: `MTIzNDU2Nzg5MDEyMzQ1Njc4.GhT9Kx.abcdefghijklmnopqrstuvwxyz1234567890`

### 🔧 Optional Secrets

#### `OWNER_IDS` (Optional)
- **Description**: Comma-separated list of Discord user IDs who have owner permissions
- **How to get your Discord ID**:
  1. Enable Developer Mode in Discord (Settings → App Settings → Advanced → Developer Mode)
  2. Right-click on your username and select "Copy User ID"
- **Example**: `123456789012345678,987654321098765432`

#### `WELCOME_CHANNEL_ID` (Optional)
- **Description**: Discord channel ID for welcome messages
- **How to get channel ID**:
  1. Enable Developer Mode in Discord
  2. Right-click on the channel and select "Copy Channel ID"
- **Example**: `1234567890123456789`

### 📝 Secret Configuration Example

```
Secret Name: DISCORD_TOKEN
Secret Value: MTIzNDU2Nzg5MDEyMzQ1Njc4.GhT9Kx.abcdefghijklmnopqrstuvwxyz1234567890

Secret Name: OWNER_IDS
Secret Value: 123456789012345678,987654321098765432

Secret Name: WELCOME_CHANNEL_ID
Secret Value: 1234567890123456789
```

### 🚀 After Adding Secrets

1. **Commit and push** your code to the `main` branch
2. **Check Actions tab** to see the deployment workflow running
3. **Monitor the deployment** in the Actions tab
4. **Verify bot status** using the workflow logs

### 🔍 Verification Steps

After deployment, you can verify your bot is working by:

1. **Invite the bot** to your Discord server with appropriate permissions
2. **Test basic commands**:
   - `?ping` - Check bot status
   - `?help` - View all commands
   - `?status` - Detailed bot information

### 🛡️ Security Best Practices

1. **Never share** your bot token publicly
2. **Regenerate token** if it's ever compromised
3. **Use repository secrets** instead of environment files
4. **Enable 2FA** on your Discord account
5. **Regularly check** who has access to your repository

### ⚠️ Troubleshooting

#### Bot not starting:
- Check if `DISCORD_TOKEN` is set correctly
- Verify token is valid in Discord Developer Portal
- Check GitHub Actions logs for error messages

#### Commands not working:
- Ensure bot has proper permissions in Discord server
- Check if Message Content Intent is enabled for your bot
- Verify bot is online in Discord

#### Deployment failing:
- Check all required secrets are configured
- Verify Python syntax is correct
- Review GitHub Actions workflow logs

### 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Review the bot's console output
3. Test commands locally first
4. Ensure Discord permissions are correct

---

**Ready to deploy! 🚀**

Once you've configured these secrets, your bot will automatically deploy when you push to the main branch.
