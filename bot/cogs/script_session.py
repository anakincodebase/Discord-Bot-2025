"""
Script Session Management Cog for Discord Bot

Author: Afnan Ahmed
Created: 2025
Description: Comprehensive script/play session management system for Discord bot
             with character assignment, role management, and voice channel integration.
             Perfect for theater groups, role-playing sessions, and dramatic readings.
Features: Character assignment, voice channel integration, session management,
          predefined play templates, and real-time role tracking.
License: MIT
"""

import discord
from discord.ext import commands
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Predefined play templates
PREDEFINED_PLAYS = {
    "a_woman_of_no_importance": {
        "title": "A Woman of No Importance",
        "author": "Oscar Wilde",
        "characters": [
            {"name": "Mrs. Arbuthnot", "description": "A woman with a secret past, the 'woman of no importance.'"},
            {"name": "Gerald Arbuthnot", "description": "Mrs. Arbuthnot's son, a young man who is offered a position as Lord Illingworth's secretary."},
            {"name": "Lord Illingworth", "description": "A powerful, witty, and flirtatious bachelor."},
            {"name": "Miss Hester Worsley", "description": "A young, puritanical American visitor."},
            {"name": "Lady Hunstanton", "description": "A wealthy, well-connected widow and hostess."},
            {"name": "Mrs. Allonby", "description": "A cynical and witty society woman."},
            {"name": "Lady Stutfield", "description": "A young widow."},
            {"name": "Lady Caroline Pontefract", "description": "A rigid and judgmental society lady."},
            {"name": "Sir John Pontefract", "description": "Lady Caroline's husband."},
            {"name": "Lord Alfred Rufford", "description": "A minor character who socializes with the others."},
            {"name": "Mr. Kelvil, M.P.", "description": "An earnest, but dull, member of Parliament."},
            {"name": "The Ven. Archdeacon Daubeny, D.D.", "description": "A member of the clergy."},
            {"name": "Farquhar", "description": "Lady Hunstanton's butler."},
            {"name": "Francis", "description": "A footman."},
            {"name": "Alice", "description": "A maid."}
        ]
    },
    "romeo_and_juliet": {
        "title": "Romeo and Juliet",
        "author": "William Shakespeare",
        "characters": [
            {"name": "Romeo", "description": "Young man from the house of Montague."},
            {"name": "Juliet", "description": "Young woman from the house of Capulet."},
            {"name": "Mercutio", "description": "Romeo's witty and loyal friend."},
            {"name": "Benvolio", "description": "Romeo's cousin and friend."},
            {"name": "Tybalt", "description": "Juliet's hot-headed cousin."},
            {"name": "Nurse", "description": "Juliet's loyal caretaker."},
            {"name": "Friar Lawrence", "description": "A wise Franciscan friar."},
            {"name": "Lord Capulet", "description": "Juliet's father."},
            {"name": "Lady Capulet", "description": "Juliet's mother."},
            {"name": "Lord Montague", "description": "Romeo's father."},
            {"name": "Lady Montague", "description": "Romeo's mother."},
            {"name": "Prince Escalus", "description": "Prince of Verona."}
        ]
    },
    "hamlet": {
        "title": "Hamlet",
        "author": "William Shakespeare",
        "characters": [
            {"name": "Hamlet", "description": "Prince of Denmark."},
            {"name": "Claudius", "description": "King of Denmark, Hamlet's uncle."},
            {"name": "Gertrude", "description": "Queen of Denmark, Hamlet's mother."},
            {"name": "Polonius", "description": "Lord Chamberlain."},
            {"name": "Laertes", "description": "Polonius's son."},
            {"name": "Ophelia", "description": "Polonius's daughter."},
            {"name": "Horatio", "description": "Hamlet's friend."},
            {"name": "Ghost of Hamlet's Father", "description": "The deceased king."},
            {"name": "Rosencrantz", "description": "Hamlet's former friend."},
            {"name": "Guildenstern", "description": "Hamlet's former friend."}
        ]
    }
}

class ScriptSessionCog(commands.Cog):
    """Cog for managing script/play sessions with character assignments."""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}  # guild_id: session_data
        
    @commands.group(name="script", aliases=["session"], invoke_without_command=True)
    async def script_session(self, ctx):
        """Main command group for script session management."""
        embed = discord.Embed(
            title="🎭 Script Session Manager",
            description="Manage your script/play sessions with ease!",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="📚 Available Commands",
            value=(
                "`?script start [title]` - Start a new custom session\n"
                "`?script templates` - View predefined plays\n"
                "`?script load <template>` - Load a predefined play\n"
                "`?script upload` - Upload custom script file\n"
                "`?script addchar <name> [description]` - Add single character\n"
                "`?script addmultiple <list>` - Add multiple characters\n"
                "`?script assign <character> <@user>` - Assign character to user\n"
                "`?script unassign <character>` - Unassign character\n"
                "`?script cast` - View current character assignments\n"
                "`?script vc` - Show voice channel participants\n"
                "`?script export [format]` - Export session to file\n"
                "`?script template <name>` - Save as reusable template\n"
                "`?script clear` - Clear session from memory\n"
                "`?script end` - End current session"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎪 Features",
            value=(
                "• Upload custom script files (.txt/.json)\n"
                "• Add characters individually or in bulk\n"
                "• Character assignment and tracking\n"
                "• Voice channel integration\n"
                "• Export sessions to files\n"
                "• Save custom templates\n"
                "• Predefined play templates\n"
                "• Real-time cast management"
            ),
            inline=False
        )
        
        embed.set_footer(text="Perfect for theater groups and role-playing sessions!")
        await ctx.send(embed=embed)
    
    @script_session.command(name="templates")
    async def show_templates(self, ctx):
        """Show available predefined play templates."""
        embed = discord.Embed(
            title="📚 Available Play Templates",
            description="Choose from these predefined plays:",
            color=discord.Color.blue()
        )
        
        for key, play in PREDEFINED_PLAYS.items():
            character_count = len(play["characters"])
            embed.add_field(
                name=f"🎭 {play['title']}",
                value=f"**Author:** {play['author']}\n**Characters:** {character_count}\n**Code:** `{key}`",
                inline=True
            )
        
        embed.add_field(
            name="💡 How to Use",
            value="Use `?script load <code>` to load a template\nExample: `?script load a_woman_of_no_importance`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="load")
    async def load_template(self, ctx, template_key: str):
        """Load a predefined play template."""
        if template_key not in PREDEFINED_PLAYS:
            await ctx.send("❌ Template not found! Use `?script templates` to see available templates.")
            return
        
        guild_id = str(ctx.guild.id)
        play_data = PREDEFINED_PLAYS[template_key]
        
        # Initialize session
        self.active_sessions[guild_id] = {
            "title": play_data["title"],
            "author": play_data["author"],
            "characters": {char["name"]: {"description": char["description"], "assigned_to": None} 
                          for char in play_data["characters"]},
            "created_by": ctx.author.id,
            "created_at": datetime.now().isoformat(),
            "voice_channel": ctx.author.voice.channel.id if ctx.author.voice else None
        }
        
        embed = discord.Embed(
            title="🎭 Session Started!",
            description=f"**{play_data['title']}** by {play_data['author']}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📋 Characters Available",
            value=f"{len(play_data['characters'])} characters ready for assignment",
            inline=True
        )
        
        embed.add_field(
            name="👥 Voice Channel",
            value=f"<#{ctx.author.voice.channel.id}>" if ctx.author.voice else "Not connected",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Next Steps",
            value=(
                "• Use `?script cast` to see all characters\n"
                "• Use `?script assign <character> <@user>` to assign roles\n"
                "• Use `?script vc` to see voice channel participants"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="start")
    async def start_session(self, ctx, *, title: str = "Custom Session"):
        """Start a new custom script session with optional title."""
        guild_id = str(ctx.guild.id)
        
        if guild_id in self.active_sessions:
            await ctx.send("❌ A session is already active! Use `?script end` to end it first.")
            return
        
        # Initialize empty session
        self.active_sessions[guild_id] = {
            "title": title,
            "author": ctx.author.display_name,
            "characters": {},
            "created_by": ctx.author.id,
            "created_at": datetime.now().isoformat(),
            "voice_channel": ctx.author.voice.channel.id if ctx.author.voice else None
        }
        
        embed = discord.Embed(
            title="🎭 Custom Session Started!",
            description=f"**{title}** session is ready!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Add Characters",
            value="Use `?script addchar <name> [description]` to add characters",
            inline=False
        )
        
        embed.add_field(
            name="📄 Upload Script",
            value="Use `?script upload` and attach a text file with character list",
            inline=False
        )
        
        embed.add_field(
            name="📚 Or Load Template",
            value="Use `?script load <template>` to load a predefined play",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="upload")
    async def upload_script(self, ctx):
        """Upload a custom script with character list from a text file."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` first to create a session.")
            return
        
        if not ctx.message.attachments:
            embed = discord.Embed(
                title="📄 Upload Custom Script",
                description="Upload a text file with your character list!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 File Format Options",
                value=(
                    "**Simple List:**\n"
                    "```\n"
                    "Character 1\n"
                    "Character 2\n"
                    "Character 3\n"
                    "```\n\n"
                    "**With Descriptions:**\n"
                    "```\n"
                    "Character 1 - Description here\n"
                    "Character 2 - Another description\n"
                    "Character 3 - Third character desc\n"
                    "```\n\n"
                    "**JSON Format:**\n"
                    "```json\n"
                    "{\n"
                    '  "title": "My Play",\n'
                    '  "author": "Author Name",\n'
                    '  "characters": [\n'
                    '    {"name": "Character 1", "description": "Desc 1"},\n'
                    '    {"name": "Character 2", "description": "Desc 2"}\n'
                    "  ]\n"
                    "}\n"
                    "```"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📤 How to Upload",
                value="Attach a `.txt` or `.json` file to your message when using this command!",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        attachment = ctx.message.attachments[0]
        
        # Check file type
        if not attachment.filename.lower().endswith(('.txt', '.json')):
            await ctx.send("❌ Please upload a `.txt` or `.json` file!")
            return
        
        try:
            # Download and read file content
            file_content = await attachment.read()
            content = file_content.decode('utf-8')
            
            session = self.active_sessions[guild_id]
            characters_added = 0
            
            if attachment.filename.lower().endswith('.json'):
                # Parse JSON format
                try:
                    data = json.loads(content)
                    if "title" in data:
                        session["title"] = data["title"]
                    if "author" in data:
                        session["author"] = data["author"]
                    
                    if "characters" in data:
                        for char in data["characters"]:
                            if isinstance(char, dict) and "name" in char:
                                char_name = char["name"]
                                char_desc = char.get("description", "No description provided")
                            else:
                                char_name = str(char)
                                char_desc = "No description provided"
                            
                            session["characters"][char_name] = {
                                "description": char_desc,
                                "assigned_to": None
                            }
                            characters_added += 1
                except json.JSONDecodeError:
                    await ctx.send("❌ Invalid JSON format! Please check your file structure.")
                    return
            else:
                # Parse text format
                lines = content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if line has description (format: "Character - Description")
                    if ' - ' in line:
                        char_name, char_desc = line.split(' - ', 1)
                        char_name = char_name.strip()
                        char_desc = char_desc.strip()
                    else:
                        char_name = line
                        char_desc = "No description provided"
                    
                    session["characters"][char_name] = {
                        "description": char_desc,
                        "assigned_to": None
                    }
                    characters_added += 1
            
            embed = discord.Embed(
                title="✅ Script Uploaded Successfully!",
                description=f"**{session['title']}** by {session['author']}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Import Summary",
                value=f"Added {characters_added} characters to the session",
                inline=True
            )
            
            embed.add_field(
                name="📋 Next Steps",
                value=(
                    "• Use `?script cast` to see all characters\n"
                    "• Use `?script assign <character> <@user>` to assign roles\n"
                    "• Use `?script vc` to check voice channel status"
                ),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error processing uploaded script: {e}")
            await ctx.send("❌ Error processing your file! Please check the format and try again.")
    
    @script_session.command(name="addmultiple", aliases=["bulk"])
    async def add_multiple_characters(self, ctx, *, characters_text: str):
        """Add multiple characters at once using text format."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        session = self.active_sessions[guild_id]
        characters_added = 0
        
        # Parse the input text
        lines = characters_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has description (format: "Character - Description")
            if ' - ' in line:
                char_name, char_desc = line.split(' - ', 1)
                char_name = char_name.strip()
                char_desc = char_desc.strip()
            else:
                char_name = line
                char_desc = "No description provided"
            
            session["characters"][char_name] = {
                "description": char_desc,
                "assigned_to": None
            }
            characters_added += 1
        
        embed = discord.Embed(
            title="✅ Characters Added!",
            description=f"Added {characters_added} characters to **{session['title']}**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="💡 Format Used",
            value=(
                "Simple format: `Character Name`\n"
                "With description: `Character Name - Description`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📋 Next Steps",
            value="Use `?script cast` to see all characters and start assigning roles!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="export")
    async def export_script(self, ctx, format_type: str = "txt"):
        """Export the current session to a file format."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session to export!")
            return
        
        session = self.active_sessions[guild_id]
        
        if format_type.lower() not in ["txt", "json"]:
            await ctx.send("❌ Format must be 'txt' or 'json'!")
            return
        
        try:
            if format_type.lower() == "json":
                # Export as JSON
                export_data = {
                    "title": session["title"],
                    "author": session["author"],
                    "created_at": session["created_at"],
                    "characters": []
                }
                
                for char_name, char_data in session["characters"].items():
                    char_export = {
                        "name": char_name,
                        "description": char_data["description"],
                        "assigned_to": None
                    }
                    
                    if char_data["assigned_to"]:
                        user_id = char_data["assigned_to"]
                        user = ctx.guild.get_member(user_id) or self.bot.get_user(user_id)
                        char_export["assigned_to"] = user.display_name if user else f"User_{user_id}"
                    
                    export_data["characters"].append(char_export)
                content = json.dumps(export_data, indent=2)
                filename = f"{session['title'].replace(' ', '_')}_script.json"
            else:
                # Export as text
                lines = [f"# {session['title']} by {session['author']}\n"]
                lines.append(f"# Created: {session['created_at'][:10]}\n")
                lines.append("# Character List:\n")
                
                for char_name, char_data in session["characters"].items():
                    assigned_info = ""
                    if char_data["assigned_to"]:
                        user_id = char_data["assigned_to"]
                        user = ctx.guild.get_member(user_id) or self.bot.get_user(user_id)
                        user_name = user.display_name if user else f"User_{user_id}"
                        assigned_info = f" (Assigned to: {user_name})"
                    
                    lines.append(f"{char_name} - {char_data['description']}{assigned_info}\n")
                
                content = "".join(lines)
                filename = f"{session['title'].replace(' ', '_')}_script.txt"
            
            # Create a file-like object
            import io
            file_obj = io.StringIO(content)
            file_obj.seek(0)
            
            # Send as attachment
            discord_file = discord.File(io.BytesIO(content.encode()), filename=filename)
            
            embed = discord.Embed(
                title="📤 Script Exported!",
                description=f"**{session['title']}** has been exported as `{filename}`",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📊 Export Details",
                value=f"Format: {format_type.upper()}\nCharacters: {len(session['characters'])}",
                inline=True
            )
            
            await ctx.send(embed=embed, file=discord_file)
            
        except Exception as e:
            logger.error(f"Error exporting script: {e}")
            await ctx.send("❌ Error exporting script! Please try again.")
    
    @script_session.command(name="template")
    async def save_as_template(self, ctx, template_name: str):
        """Save the current session as a reusable template."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session to save as template!")
            return
        
        session = self.active_sessions[guild_id]
        
        if not session["characters"]:
            await ctx.send("❌ Cannot save empty session as template! Add some characters first.")
            return
        
        # Create template format
        template_data = {
            "title": session["title"],
            "author": session["author"],
            "characters": [
                {
                    "name": char_name,
                    "description": char_data["description"]
                }
                for char_name, char_data in session["characters"].items()
            ]
        }
        
        # Add to predefined plays (in memory for this session)
        template_key = template_name.lower().replace(" ", "_")
        PREDEFINED_PLAYS[template_key] = template_data
        
        embed = discord.Embed(
            title="✅ Template Saved!",
            description=f"**{session['title']}** saved as template `{template_key}`",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📋 Template Details",
            value=f"Characters: {len(session['characters'])}\nCode: `{template_key}`",
            inline=True
        )
        
        embed.add_field(
            name="🔄 How to Use",
            value=f"Use `?script load {template_key}` to load this template in future sessions",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Note",
            value="Template is saved for this bot session only. Export to file for permanent storage.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="addchar")
    async def add_character(self, ctx, character_name: str, *, description: str = "No description provided"):
        """Add a character to the current session."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        self.active_sessions[guild_id]["characters"][character_name] = {
            "description": description,
            "assigned_to": None
        }
        
        embed = discord.Embed(
            title="✅ Character Added!",
            description=f"**{character_name}** has been added to the session.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Description",
            value=description,
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="assign")
    async def assign_character(self, ctx, character_name: str, user: discord.Member):
        """Assign a character to a user."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        session = self.active_sessions[guild_id]
        
        # Find character (case-insensitive)
        character_key = None
        for char in session["characters"]:
            if char.lower() == character_name.lower():
                character_key = char
                break
        
        if not character_key:
            await ctx.send(f"❌ Character '{character_name}' not found in this session!")
            return
        
        # Check if character is already assigned
        if session["characters"][character_key]["assigned_to"]:
            current_user_id = session["characters"][character_key]["assigned_to"]
            current_user = ctx.guild.get_member(current_user_id) or self.bot.get_user(current_user_id)
            user_display = current_user.mention if current_user else f"<@{current_user_id}>"
            await ctx.send(f"❌ {character_key} is already assigned to {user_display}!")
            return
        
        # Assign character
        session["characters"][character_key]["assigned_to"] = user.id
        
        embed = discord.Embed(
            title="🎭 Character Assigned!",
            description=f"**{character_key}** has been assigned to {user.mention}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Character Description",
            value=session["characters"][character_key]["description"],
            inline=False
        )
        
        # Check if user is in voice channel
        if user.voice and session.get("voice_channel"):
            if user.voice.channel.id == session["voice_channel"]:
                embed.add_field(
                    name="🔊 Voice Status",
                    value="✅ User is in the session voice channel",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🔊 Voice Status",
                    value="⚠️ User is in a different voice channel",
                    inline=True
                )
        else:
            embed.add_field(
                name="🔊 Voice Status",
                value="❌ User not in voice channel",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="unassign")
    async def unassign_character(self, ctx, character_name: str):
        """Unassign a character."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        session = self.active_sessions[guild_id]
        
        # Find character (case-insensitive)
        character_key = None
        for char in session["characters"]:
            if char.lower() == character_name.lower():
                character_key = char
                break
        
        if not character_key:
            await ctx.send(f"❌ Character '{character_name}' not found in this session!")
            return
        
        if not session["characters"][character_key]["assigned_to"]:
            await ctx.send(f"❌ {character_key} is not assigned to anyone!")
            return
        
        # Unassign character
        session["characters"][character_key]["assigned_to"] = None
        
        embed = discord.Embed(
            title="✅ Character Unassigned!",
            description=f"**{character_key}** is now available for assignment.",
            color=discord.Color.orange()
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="cast")
    async def show_cast(self, ctx):
        """Show current character assignments."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        session = self.active_sessions[guild_id]
        
        embed = discord.Embed(
            title=f"🎭 Cast for '{session['title']}'",
            description=f"Author: {session['author']}",
            color=discord.Color.purple()
        )
        
        assigned_chars = []
        unassigned_chars = []
        
        for char_name, char_data in session["characters"].items():
            if char_data["assigned_to"]:
                user_id = char_data["assigned_to"]
                user = ctx.guild.get_member(user_id) or self.bot.get_user(user_id)
                voice_status = "🔊" if user and user.voice else "🔇"
                user_display = user.mention if user else f"<@{user_id}>"
                assigned_chars.append(f"{voice_status} **{char_name}** → {user_display}")
            else:
                unassigned_chars.append(f"• **{char_name}**")
        
        if assigned_chars:
            embed.add_field(
                name="✅ Assigned Characters",
                value="\n".join(assigned_chars),
                inline=False
            )
        
        if unassigned_chars:
            embed.add_field(
                name="❌ Unassigned Characters",
                value="\n".join(unassigned_chars),
                inline=False
            )
        
        if not assigned_chars and not unassigned_chars:
            embed.add_field(
                name="📝 No Characters",
                value="Use `?script addchar` to add characters or `?script load` to load a template.",
                inline=False
            )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"Assigned: {len(assigned_chars)} | Unassigned: {len(unassigned_chars)} | Total: {len(session['characters'])}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="vc")
    async def show_voice_channel(self, ctx):
        """Show voice channel participants and their character assignments."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        session = self.active_sessions[guild_id]
        
        if not session.get("voice_channel"):
            await ctx.send("❌ No voice channel associated with this session!")
            return
        
        voice_channel = self.bot.get_channel(session["voice_channel"])
        if not voice_channel:
            await ctx.send("❌ Associated voice channel not found!")
            return
        
        embed = discord.Embed(
            title=f"🔊 Voice Channel: {voice_channel.name}",
            description=f"Session: **{session['title']}**",
            color=discord.Color.blue()
        )
        
        participants = []
        assigned_users = set()
        
        # Get character assignments for quick lookup
        user_to_character = {}
        for char_name, char_data in session["characters"].items():
            if char_data["assigned_to"]:
                user_to_character[char_data["assigned_to"]] = char_name
                assigned_users.add(char_data["assigned_to"])
        
        # Check voice channel members
        for member in voice_channel.members:
            character = user_to_character.get(member.id, "No character assigned")
            status = "🎭" if member.id in assigned_users else "👤"
            participants.append(f"{status} {member.mention} → **{character}**")
        
        if participants:
            embed.add_field(
                name="👥 Participants",
                value="\n".join(participants),
                inline=False
            )
        else:
            embed.add_field(
                name="👥 Participants",
                value="No one is currently in the voice channel.",
                inline=False
            )
        
        # Show users with characters not in VC
        not_in_vc = []
        for user_id in assigned_users:
            user = ctx.guild.get_member(user_id) or self.bot.get_user(user_id)
            if user and (not user.voice or user.voice.channel.id != session["voice_channel"]):
                character = user_to_character[user_id]
                user_display = user.mention if user else f"<@{user_id}>"
                not_in_vc.append(f"🎭 {user_display} → **{character}**")
            elif not user:
                # Handle case where user is not found
                character = user_to_character[user_id]
                not_in_vc.append(f"🎭 <@{user_id}> → **{character}**")
        
        if not_in_vc:
            embed.add_field(
                name="⚠️ Assigned but not in VC",
                value="\n".join(not_in_vc),
                inline=False
            )
        
        embed.add_field(
            name="📊 Summary",
            value=f"In VC: {len(participants)} | Assigned roles: {len(assigned_users)} | Total characters: {len(session['characters'])}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="end")
    async def end_session(self, ctx):
        """End the current script session."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session to end!")
            return
        
        session = self.active_sessions[guild_id]
        
        # Only session creator or admins can end
        if ctx.author.id != session["created_by"] and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Only the session creator or administrators can end the session!")
            return
        
        # Create summary
        assigned_count = sum(1 for char in session["characters"].values() if char["assigned_to"])
        total_count = len(session["characters"])
        
        embed = discord.Embed(
            title="🎭 Session Ended",
            description=f"**{session['title']}** session has ended.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="📊 Final Statistics",
            value=f"Characters assigned: {assigned_count}/{total_count}",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Duration",
            value=f"Started: {session['created_at'][:10]}",
            inline=True
        )
        
        embed.add_field(
            name="👑 Created by",
            value=f"<@{session['created_by']}>",
            inline=True
        )
        
        # Remove session
        del self.active_sessions[guild_id]
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="clear", aliases=["reset"])
    async def clear_session(self, ctx):
        """Clear the current script session and remove it from memory."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session to clear!")
            return
        
        session = self.active_sessions[guild_id]
        
        # Only session creator or admins can clear
        if ctx.author.id != session["created_by"] and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Only the session creator or administrators can clear the session!")
            return
        
        # Get session info before clearing
        session_title = session["title"]
        character_count = len(session["characters"])
        assigned_count = sum(1 for char in session["characters"].values() if char["assigned_to"])
        
        # Remove session from memory
        del self.active_sessions[guild_id]
        
        embed = discord.Embed(
            title="🧹 Session Cleared!",
            description=f"**{session_title}** has been cleared from memory.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="📊 Cleared Data",
            value=f"Characters: {character_count}\nAssignments: {assigned_count}",
            inline=True
        )
        
        embed.add_field(
            name="✨ Ready for New Session",
            value="You can now start a new session with `?script start` or load a template with `?script load`",
            inline=False
        )
        
        embed.add_field(
            name="💡 Note",
            value="All character assignments and session data have been permanently removed.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @script_session.command(name="info")
    async def session_info(self, ctx):
        """Show detailed information about the current session."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.active_sessions:
            await ctx.send("❌ No active session! Use `?script start` or `?script load` first.")
            return
        
        session = self.active_sessions[guild_id]
        
        embed = discord.Embed(
            title=f"📋 Session Info: {session['title']}",
            description=f"Author: {session['author']}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="👑 Created by",
            value=f"<@{session['created_by']}>",
            inline=True
        )
        
        embed.add_field(
            name="📅 Created",
            value=session['created_at'][:10],
            inline=True
        )
        
        voice_channel = self.bot.get_channel(session["voice_channel"]) if session.get("voice_channel") else None
        embed.add_field(
            name="🔊 Voice Channel",
            value=f"<#{voice_channel.id}>" if voice_channel else "None",
            inline=True
        )
        
        assigned_count = sum(1 for char in session["characters"].values() if char["assigned_to"])
        total_count = len(session["characters"])
        
        embed.add_field(
            name="📊 Progress",
            value=f"{assigned_count}/{total_count} characters assigned",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ScriptSessionCog(bot))
