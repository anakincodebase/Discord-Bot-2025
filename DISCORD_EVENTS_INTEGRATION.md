# 🌐 Discord Events Integration

## Overview
The bot now creates **Discord native server events** when users use `?createevent`, making events appear in Discord's official Events tab alongside the bot's custom RSVP system.

## How It Works

### Dual Event System
When you create an event with `?createevent`, the bot:

1. ✅ **Creates a bot-managed event** with RSVP buttons and tracking
2. 🌐 **Creates a Discord server event** that appears in the Events tab
3. 🔗 **Links both events** for unified management

### What Users See
- **Discord Events Tab**: Official server event with Discord's native interface
- **Bot Event Message**: Interactive RSVP buttons and detailed tracking
- **Unified Management**: Both events are cancelled together

## Required Permissions

### Bot Permissions Needed
The bot needs the **"Manage Events"** permission to create Discord server events.

### Permission Setup
1. Go to **Server Settings** → **Roles**
2. Find your bot's role
3. Enable **"Manage Events"** permission
4. Save changes

### Check Permissions
Use `?eventperms` to check if the bot has the required permissions.

## Command Usage

### Create Event (Enhanced)
```
?createevent "Game Night" "Weekly gaming session" 2025-12-25 19:00 120
```

**Now creates:**
- ✅ Bot event with RSVP system
- 📅 Discord server event in Events tab
- 🔗 Link between both events

### Success Response
```
✅ Event Created Successfully!

📅 Discord Event: Created in server events
🔗 Event Link: [View in Discord Events](https://discord.com/events/123/456)
🆔 Bot Event ID: abc123
⏰ Reminders: Will be sent 30 minutes before the event
```

### Permission Check
```
?eventperms
```
Shows current bot permissions and setup instructions.

## Features

### Enhanced Event Creation
- **Discord Integration**: Events appear in server's Events tab
- **Direct Links**: Links to view events in Discord's interface
- **Unified Cancellation**: Cancelling bot event also cancels Discord event
- **Permission Validation**: Automatic checking and helpful error messages

### Fallback Behavior
If the bot lacks permissions:
- ⚠️ **Bot event still created** with full RSVP functionality
- ❌ **Discord event not created** (with clear explanation)
- 💡 **Helpful instructions** to enable permissions

### Event Display
Events now show:
```
🌐 Discord Event: ✅ Created in server events
```
or
```
🌐 Discord Event: ❌ Failed to create (check permissions)
```

## Benefits

### For Users
- **Native Discord Experience**: Events appear where users expect them
- **Dual Interface**: Choose between Discord's interface or bot's RSVP system
- **Better Discovery**: Events visible in Discord's Events tab
- **Mobile Support**: Full mobile app integration

### For Server Admins
- **Professional Appearance**: Events look official in Discord
- **Better Engagement**: Users more likely to see and join events
- **Unified Management**: Single command creates both event types
- **Permission Control**: Clear setup and troubleshooting

## Technical Implementation

### Event Linking
```python
class EventData:
    # ... existing fields ...
    discord_event_id: Optional[int] = None  # Links to Discord event
```

### Creation Process
1. Parse user input and validate
2. Create bot event with RSVP system
3. Create Discord server event (if permissions allow)
4. Link both events by storing Discord event ID
5. Display success message with links

### Error Handling
- **Permission Errors**: Clear explanation and setup instructions
- **API Errors**: Graceful fallback to bot-only events
- **Rate Limits**: Proper error handling and user feedback

## Migration

### Existing Events
- Old events continue to work normally
- No Discord events for pre-existing bot events
- New events get both systems

### Upgrading
No user action required - enhancement is automatic for new events.

## Commands Summary

| Command | Description | Discord Integration |
|---------|-------------|-------------------|
| `?createevent` | Create event | ✅ Creates Discord event |
| `?events` | List events | Shows both types |
| `?eventinfo` | Event details | Shows Discord status |
| `?cancelevent` | Cancel event | Cancels both events |
| `?eventperms` | Check permissions | Setup validation |

## Troubleshooting

### "Failed to create Discord event"
1. Check bot has "Manage Events" permission
2. Run `?eventperms` for detailed status
3. Follow permission setup instructions
4. Bot events still work without Discord integration

### Discord event not cancelled
- May require manual cancellation in Discord
- Check bot permissions
- Contact server admin for help

### Events not appearing in Events tab
- Verify bot has "Manage Events" permission
- Check if event was created successfully
- Look for error messages in bot response

---