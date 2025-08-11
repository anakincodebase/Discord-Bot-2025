# Event Creation and Management System

## Overview
The Events system provides comprehensive event creation and management functionality for Discord servers. Users can create events, manage RSVPs, and receive automated reminders.

## Features

### 🎯 Event Creation
- Create events with both text commands (`?createevent`) and slash commands (`/createevent`)
- Set event title, description, date, time, and duration
- Flexible date/time parsing supporting multiple formats
- Automatic validation to prevent past events

### 👥 RSVP System
- Interactive buttons for RSVP responses
- Three response options: Attending (✅), Maybe (❓), Not Attending (❌)
- Real-time RSVP count updates
- Persistent RSVP tracking across bot restarts

### ⏰ Automated Reminders
- Automatic reminders sent 30 minutes before events
- Mentions all attending participants
- Background task runs every 5 minutes to check for upcoming events

### 📊 Event Management
- List all upcoming events in a server
- View detailed event information
- Cancel events (creator or admin only)
- Persistent event storage across bot restarts

## Commands

### Create Event
```
?createevent <title> <description> <date> <time> [duration]
/createevent <title> <description> <date> <time> [duration]
```

**Parameters:**
- `title`: Event title (required)
- `description`: Event description (required)
- `date`: Event date (required) - See supported formats below
- `time`: Event time (required) - See supported formats below
- `duration`: Duration in minutes (optional, default: 60)

**Example:**
```
?createevent "Team Meeting" "Weekly sync meeting" 2025-12-25 14:30 90
/createevent title:Team Meeting description:Weekly sync meeting date:2025-12-25 time:14:30 duration:90
```

### List Events
```
?events
/events
```
Shows all upcoming events in the current server, sorted by start time.

### Event Information
```
?eventinfo <event_id>
/eventinfo <event_id>
```
Display detailed information about a specific event with RSVP buttons.

### Cancel Event
```
?cancelevent <event_id>
/cancelevent <event_id>
```
Cancel an event (only event creator or server administrators can cancel events).

## Supported Date Formats

### Date Formats
- `YYYY-MM-DD` (e.g., 2025-12-25)
- `MM/DD/YYYY` (e.g., 12/25/2025)
- `DD/MM/YYYY` (e.g., 25/12/2025)
- `MM-DD-YYYY` (e.g., 12-25-2025)
- `DD-MM-YYYY` (e.g., 25-12-2025)

### Time Formats
- `HH:MM` (24-hour format, e.g., 14:30)
- `H:MM AM/PM` (12-hour format, e.g., 2:30 PM)
- `H:MMAM/PM` (12-hour format without space, e.g., 2:30PM)
- `HH.MM` (24-hour with dots, e.g., 14.30)

## RSVP System

### Response Options
- **✅ Attending**: Confirms attendance
- **❓ Maybe**: Indicates possible attendance
- **❌ Not Attending**: Confirms non-attendance

### Features
- Users can change their RSVP at any time
- Real-time updates to attendance counts
- Automatic removal from other categories when selecting a new option
- Persistent storage of RSVP data

## Event Data Structure

### EventData Class
```python
class EventData:
    event_id: str               # Unique 8-character identifier
    title: str                  # Event title
    description: str            # Event description
    creator_id: int            # Discord user ID of creator
    guild_id: int              # Discord server ID
    channel_id: int            # Discord channel ID where created
    start_time: datetime       # Event start time (UTC)
    duration_minutes: int      # Event duration in minutes
    created_at: datetime       # Creation timestamp
    participants: List[int]    # List of attending user IDs
    maybe_participants: List[int]  # List of maybe attending user IDs
    not_attending: List[int]   # List of not attending user IDs
    is_cancelled: bool         # Cancellation status
    reminder_sent: bool        # Reminder notification status
```

## Storage

### File Storage
- Events are stored in `bot_events.json` file
- Automatic saving after RSVP changes
- Persistence across bot restarts
- JSON format for easy debugging and backup

### Data Persistence
- All event data is automatically saved
- RSVP changes are immediately persisted
- Events survive bot restarts and updates

## Permissions

### Event Creation
- Any user can create events
- No special permissions required

### Event Management
- Event creators can cancel their own events
- Server administrators can cancel any event
- Only creators and admins have management access

### RSVP System
- Any user can respond to events
- No restrictions on RSVP changes
- Real-time updates for all users

## Error Handling

### Validation
- Past date/time validation
- Duration limits (1-1440 minutes)
- Date/time format validation
- Permission checks for cancellation

### User Feedback
- Clear error messages for invalid inputs
- Helpful format examples for date/time
- Permission denied notifications
- Success confirmations for actions

## Automation Features

### Reminder System
- Background task checks every 5 minutes
- Reminders sent 30 minutes before events
- Automatic mention of attending participants
- One-time reminder per event

### Status Updates
- Real-time RSVP count updates
- Time remaining calculations
- Event status indicators
- Automatic embed refreshing

## Technical Implementation

### Dependencies
- `discord.py` for Discord integration
- `asyncio` for asynchronous operations
- `json` for data persistence
- `datetime` for time management
- `uuid` for unique ID generation

### Cog Structure
- Separate cog file (`events.py`) for modularity
- Hybrid commands supporting both text and slash commands
- Interactive UI components with discord.ui.View
- Background tasks for automation

### Integration
- Seamlessly integrates with existing bot structure
- Added to main deployment configuration
- Included in help command suggestions
- Compatible with existing cog loading system

## Usage Examples

### Creating a Simple Event
```
?createevent "Game Night" "Weekly board game session" 2025-08-15 19:00
```

### Creating a Long Event
```
?createevent "Conference" "Annual tech conference" 2025-09-20 09:00 480
```

### Using Slash Commands
```
/createevent title:Workshop description:Python workshop date:2025-08-20 time:2:00 PM duration:120
```

### Managing Events
```
?events                    # List all upcoming events
?eventinfo abc123def       # View specific event details
?cancelevent abc123def     # Cancel an event
```

## Best Practices

### Event Creation
- Use descriptive titles and descriptions
- Include all relevant information in the description
- Choose appropriate durations
- Double-check date and time before creating

### RSVP Management
- Update RSVP status if plans change
- Use "Maybe" for uncertain attendance
- Check event details before responding

### Event Organization
- Create events well in advance
- Include location information in descriptions
- Use clear, specific titles
- Set realistic durations

## Troubleshooting

### Common Issues
1. **Invalid Date Format**: Use supported formats listed above
2. **Past Date Error**: Ensure event is in the future
3. **Permission Denied**: Only creators and admins can cancel events
4. **Event Not Found**: Double-check the event ID

### Support
- Use `?help createevent` for command help
- Check date/time format examples
- Verify permissions for event management
- Contact server administrators for issues

## Future Enhancements

### Planned Features
- Recurring events
- Event categories and tags
- Advanced notification settings
- Calendar integration
- Event templates
- Location and voice channel integration
- Export functionality
- Advanced permission controls

### Community Feedback
- User suggestions welcome
- Feature requests considered
- Bug reports appreciated
- Performance feedback valued
