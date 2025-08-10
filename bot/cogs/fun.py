"""
Fun commands and games for the Discord bot.

Author: Afnan Ahmed
Created: 2025
Description: Interactive entertainment and social commands including games,
             trivia, hangman, ship calculator, and various fun interactions.
Features: Permission-based commands, interactive UI elements, 
          image processing, GIF integration, gaming systems.
License: MIT
"""

import asyncio
import io
import os
import random
import re
from typing import Dict, List

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from bot.helpers.hangman_game import HangmanGame
from bot.helpers.trivia_data import trivia_questions

class HangmanSelect(discord.ui.Select):
    """Select dropdown for Hangman letter selection."""
    
    def __init__(self, options):
        super().__init__(
            placeholder="Choose a letter...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view: HangmanView = self.view
        letter = self.values[0].lower()
        
        for child in view.children:
            child.disabled = True

        correct, result = view.game.guess(letter)

        embed = discord.Embed(
            title="🎯 Hangman Game",
            color=discord.Color.purple()
        )
        embed.add_field(name="Word", value=view.game.get_display(), inline=False)
        embed.add_field(name="Attempts Left", value=str(view.game.attempts), inline=True)
        embed.add_field(name="Visual", value=f"```{view.game.get_visual()}```", inline=False)
        embed.add_field(name="Guessed Letters", value=view.game.get_guessed(), inline=True)
        embed.add_field(name="Hint", value=view.game.hint, inline=False)
        embed.set_footer(text=f"You guessed: '{letter}' ({result})")

        if view.game.is_won():
            embed.title = "🎉 You Won!"
            embed.color = discord.Color.green()
            embed.set_footer(text=f"The word was: {view.game.word.upper()}")
            view.stop()
        elif view.game.is_lost():
            embed.title = "💀 You Lost!"
            embed.color = discord.Color.red()
            embed.set_footer(text=f"The word was: {view.game.word.upper()}")
            view.stop()

        # Remove guessed letter
        for select in view.selects:
            select.options = [opt for opt in select.options if opt.value.lower() != letter]
            if not view.game.is_won() and not view.game.is_lost():
                select.disabled = False

        await interaction.response.edit_message(embed=embed, view=view)

class HangmanView(discord.ui.View):
    """View for Hangman game interface."""
    
    def __init__(self, game: HangmanGame):
        super().__init__(timeout=90)
        self.game = game
        self.selects = [
            HangmanSelect([discord.SelectOption(label=chr(c), value=chr(c)) for c in range(ord('A'), ord('N'))]),
            HangmanSelect([discord.SelectOption(label=chr(c), value=chr(c)) for c in range(ord('N'), ord('Z') + 1)])
        ]
        for select in self.selects:
            self.add_item(select)
        self.message = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(content="⏰ Game timed out!", view=self)

class TicTacToeButton(discord.ui.Button):
    """Enhanced button for Tic-Tac-Toe game with improved visuals."""
    
    def __init__(self, position: int):
        # Use position numbers as labels initially for better UX
        super().__init__(
            style=discord.ButtonStyle.secondary, 
            label=str(position + 1),  # Show position numbers 1-9
            row=position // 3
        )
        self.position = position
        self.is_empty = True

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe = self.view
        
        # Check if it's the correct player's turn
        if interaction.user != view.current_player:
            await interaction.response.send_message(
                f"⚠️ It's not your turn! It's {view.current_player.mention}'s turn.", 
                ephemeral=True
            )
            return

        # Check if cell is already taken
        if not self.is_empty:
            await interaction.response.send_message(
                "❌ This cell is already taken! Choose another one.", 
                ephemeral=True
            )
            return

        # Make the move
        current_symbol = view.symbols[view.current_player_index]
        self.label = current_symbol
        self.style = discord.ButtonStyle.danger if view.current_player_index == 0 else discord.ButtonStyle.success
        self.is_empty = False
        view.board[self.position] = current_symbol
        view.move_count += 1

        # Check for win condition
        if view.check_win(current_symbol):
            await view.handle_game_end(interaction, "win")
            return
        elif view.move_count >= 9:
            await view.handle_game_end(interaction, "draw")
            return
        else:
            # Switch to next player
            view.current_player_index = 1 - view.current_player_index
            view.current_player = view.players[view.current_player_index]
            await view.update_game_display(interaction)

class TicTacToeRematchButton(discord.ui.Button):
    """Button for rematch functionality."""
    
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="🔄 Rematch",
            emoji="🔄"
        )
    
    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe = self.view
        
        # Only the players can start a rematch
        if interaction.user not in view.players:
            await interaction.response.send_message(
                "❌ Only the players can start a rematch!", 
                ephemeral=True
            )
            return
        
        # Start a new game
        new_view = TicTacToe(view.players[0], view.players[1])
        new_embed = new_view.create_game_embed()
        
        await interaction.response.edit_message(embed=new_embed, view=new_view)
        new_view.message = interaction.message

class TicTacToe(discord.ui.View):
    """Enhanced Tic-Tac-Toe game with dynamic features and better UX."""
    
    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.players = [player1, player2]
        self.symbols = ["❌", "⭕"]
        self.current_player_index = 0
        self.current_player = self.players[0]
        self.board = [None] * 9
        self.move_count = 0
        self.game_over = False
        self.winner = None
        self.message = None
        
        # Create the 3x3 grid of buttons
        for i in range(9):
            self.add_item(TicTacToeButton(i))

    def create_game_embed(self):
        """Create a dynamic embed showing current game state."""
        if self.game_over:
            if self.winner:
                title = f"🎉 {self.winner.display_name} Wins!"
                color = discord.Color.gold()
                description = f"🏆 **Winner:** {self.winner.mention}\n📊 **Moves:** {self.move_count}"
            else:
                title = "🤝 It's a Draw!"
                color = discord.Color.orange()
                description = f"🤝 **Result:** Draw\n📊 **Total Moves:** {self.move_count}"
        else:
            title = "⭕ Tic-Tac-Toe Game"
            color = discord.Color.blurple()
            current_symbol = self.symbols[self.current_player_index]
            description = (
                f"🎮 **Players:** {self.players[0].mention} ({self.symbols[0]}) vs {self.players[1].mention} ({self.symbols[1]})\n"
                f"🎯 **Current Turn:** {self.current_player.mention} ({current_symbol})\n"
                f"📊 **Move Count:** {self.move_count}/9"
            )
        
        embed = discord.Embed(title=title, description=description, color=color)
        
        # Add visual board representation
        board_visual = self.get_board_visual()
        embed.add_field(name="📋 Game Board", value=board_visual, inline=False)
        
        if not self.game_over:
            embed.add_field(
                name="💡 How to Play", 
                value="Click the numbered buttons to make your move!", 
                inline=False
            )
            embed.set_footer(text="⏱️ Game will timeout in 5 minutes if inactive")
        else:
            embed.set_footer(text="🎮 Click rematch to play again!")
        
        return embed

    def get_board_visual(self):
        """Create a visual representation of the board."""
        visual_board = []
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                pos = i + j
                if self.board[pos]:
                    row.append(self.board[pos])
                else:
                    row.append(f"`{pos + 1}`")
            visual_board.append(" │ ".join(row))
        
        return "\n" + "─" * 13 + "\n" + f"\n{' ' * 4}─────\n".join(visual_board) + "\n" + "─" * 13

    def check_win(self, symbol: str):
        """Check if the given symbol has won the game."""
        b = self.board
        win_combos = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
            (0, 4, 8), (2, 4, 6)              # diagonals
        ]
        return any(b[a] == b[b_idx] == b[c] == symbol for a, b_idx, c in win_combos)

    async def handle_game_end(self, interaction: discord.Interaction, result: str):
        """Handle the end of the game with enhanced feedback."""
        self.game_over = True
        
        # Disable all game buttons
        for child in self.children:
            if isinstance(child, TicTacToeButton):
                child.disabled = True
        
        if result == "win":
            self.winner = self.current_player
            # Highlight winning combination
            self.highlight_winning_combination()
        
        # Add rematch button
        self.add_item(TicTacToeRematchButton())
        
        # Update display
        embed = self.create_game_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def highlight_winning_combination(self):
        """Highlight the winning combination on the board."""
        if not self.winner:
            return
        
        symbol = self.symbols[self.current_player_index]
        b = self.board
        win_combos = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
            (0, 4, 8), (2, 4, 6)              # diagonals
        ]
        
        for combo in win_combos:
            if all(b[pos] == symbol for pos in combo):
                for pos in combo:
                    for child in self.children:
                        if isinstance(child, TicTacToeButton) and child.position == pos:
                            child.style = discord.ButtonStyle.primary
                break

    async def update_game_display(self, interaction: discord.Interaction):
        """Update the game display with current state."""
        embed = self.create_game_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        """Handle timeout with enhanced feedback."""
        self.game_over = True
        for child in self.children:
            child.disabled = True
        
        embed = discord.Embed(
            title="⏰ Game Timed Out",
            description=f"The game between {self.players[0].mention} and {self.players[1].mention} has timed out.",
            color=discord.Color.red()
        )
        embed.add_field(name="📊 Final State", value=f"Moves made: {self.move_count}/9", inline=False)
        embed.set_footer(text="Start a new game with ?tictactoe @user")
        
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass

class FunCog(commands.Cog):
    """Fun commands and games cog."""
    
    def __init__(self, bot):
        self.bot = bot
        self.current_trivia = {}  # Store trivia questions per channel

    def create_circular_image(self, data, size=(300, 300)):
        """Create a circular image from image data."""
        img = Image.open(io.BytesIO(data)).convert("RGBA").resize(size)
        scale = 4
        big_size = (size[0] * scale, size[1] * scale)
        mask = Image.new("L", big_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + big_size, fill=255)
        mask = mask.resize(size, Image.LANCZOS)
        circular = Image.new("RGBA", size)
        circular.paste(img, (0, 0), mask)
        return circular

    @commands.command(name="hangman")
    async def hangman(self, ctx):
        """Start a Hangman game."""
        game = HangmanGame()
        view = HangmanView(game)

        embed = discord.Embed(
            title="🎯 Hangman Game Started!",
            description="Guess the word using the menus below.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Word", value=game.get_display(), inline=False)
        embed.add_field(name="Attempts Left", value=str(game.attempts), inline=True)
        embed.add_field(name="Visual", value=f"```{game.get_visual()}```", inline=False)
        embed.add_field(name="Hint", value=game.hint, inline=False)

        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

    @commands.command(name="tictactoe")
    async def tictactoe(self, ctx, opponent: discord.Member):
        """Start an enhanced Tic-Tac-Toe game with dynamic features."""
        # Validation checks
        if opponent.bot:
            embed = discord.Embed(
                title="❌ Invalid Opponent",
                description="You cannot play against a bot! Challenge a real player instead.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
            
        if opponent == ctx.author:
            embed = discord.Embed(
                title="❌ Invalid Opponent", 
                description="You cannot play against yourself! Challenge someone else.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Create the enhanced game
        view = TicTacToe(ctx.author, opponent)
        embed = view.create_game_embed()
        
        # Send initial game message
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg
        
        # Send a ping to the opponent
        ping_embed = discord.Embed(
            description=f"🎮 {opponent.mention}, you've been challenged to Tic-Tac-Toe by {ctx.author.mention}!",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=ping_embed, delete_after=10)

    @app_commands.command(name="tictactoe", description="Challenge someone to an enhanced Tic-Tac-Toe game!")
    async def tictactoe_slash(self, interaction: discord.Interaction, opponent: discord.Member):
        """Slash command version of Tic-Tac-Toe."""
        # Validation checks
        if opponent.bot:
            embed = discord.Embed(
                title="❌ Invalid Opponent",
                description="You cannot play against a bot! Challenge a real player instead.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        if opponent == interaction.user:
            embed = discord.Embed(
                title="❌ Invalid Opponent", 
                description="You cannot play against yourself! Challenge someone else.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create the enhanced game
        view = TicTacToe(interaction.user, opponent)
        embed = view.create_game_embed()
        
        # Send initial game message
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        
        # Send a follow-up ping to the opponent
        ping_embed = discord.Embed(
            description=f"🎮 {opponent.mention}, you've been challenged to Tic-Tac-Toe by {interaction.user.mention}!",
            color=discord.Color.blurple()
        )
        await interaction.followup.send(embed=ping_embed, ephemeral=False)

    @commands.command(name="trivia")
    async def trivia(self, ctx):
        """Start a trivia question."""
        if ctx.channel.id in self.current_trivia:
            await ctx.send("A trivia question is already active in this channel!")
            return

        question_data = random.choice(trivia_questions)
        question = question_data["question"]
        answer = question_data["answer"].lower()
        
        self.current_trivia[ctx.channel.id] = {
            "answer": answer,
            "asker": ctx.author
        }

        embed = discord.Embed(
            title="🧠 Trivia Time!",
            description=question,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Type your answer in chat! (30 seconds)")
        
        await ctx.send(embed=embed)
        
        # Wait for answer
        def check(m):
            return (m.channel == ctx.channel and 
                   not m.author.bot and 
                   ctx.channel.id in self.current_trivia)

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
            user_answer = msg.content.lower().strip()
            
            if user_answer == answer:
                embed = discord.Embed(
                    title="🎉 Correct!",
                    description=f"{msg.author.mention} got it right!\\nThe answer was: **{answer}**",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                # Check if it's close
                if answer in user_answer or user_answer in answer:
                    embed = discord.Embed(
                        title="❌ Close, but not quite!",
                        description=f"The correct answer was: **{answer}**",
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ Incorrect!",
                        description=f"The correct answer was: **{answer}**",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Time's up!",
                description=f"The correct answer was: **{answer}**",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed)
        finally:
            del self.current_trivia[ctx.channel.id]

    @commands.command(name="ship")
    async def ship(self, ctx, user1: discord.Member = None, user2: discord.Member = None):
        """Calculate love compatibility between two users."""
        mentioned_users = ctx.message.mentions
        
        if len(mentioned_users) == 0:
            await ctx.send(f"💔 {ctx.author.mention}, you must mention at least one user to calculate love compatibility!")
            return

        if len(mentioned_users) == 1:
            user1 = ctx.author
            user2 = mentioned_users[0]
        else:
            user1, user2 = mentioned_users[:2]
        
        # Generate compatibility score
        base_score = random.randint(0, 100)
        if len(user1.name) == len(user2.name):
            base_score = min(100, base_score + random.randint(10, 20))
        compatibility_score = min(100, base_score)

        def get_heart_and_comment(score):
            if score == 100:
                return "<:LuxiriaTenshi_Heart:1363881448230096948>", " It's PERFECT! You two are a match made in heaven!", "https://example.com/perfect.gif"
            elif score >= 90:
                return "<a:Heart:1363881614664400986>", "✨ Absolutely destined souls!", "https://example.com/destined.gif"
            elif score >= 70:
                return "<a:Heart:1363881614664400986>", "Something special is brewing...", "https://example.com/special.gif"
            elif score >= 50:
                return "<a:Heart:1363881614664400986>", "There's a spark worth igniting.", "https://example.com/spark.gif"
            elif score >= 30:
                return "<:broken_heartpulse:1363882089262354482>", "The flame flickers, but it's not too bright...", "https://example.com/flicker.gif"
            else:
                return "<a:Alert:1363632747616407733>", "Not quite a match—perhaps best as friends.", "https://example.com/friends.gif"

        heart_emoji, message_comment, gif_url = get_heart_and_comment(compatibility_score)

        def build_love_bar(score, segments=11):
            score_text = f"{score}%"
            center_index = segments // 2
            bar = []
            filled = segments if score == 100 else round((score / 100) * (segments - 1))
            
            for i in range(segments):
                if i == center_index:
                    bar.append(f"✨`{score_text}`✨")
                elif i < filled:
                    bar.append("<a:8837redfireflames:1363876518023135302>")
                else:
                    bar.append("<a:1463lightmintfireflames:1363876611715498267>")
            return ''.join(bar)

        love_bar = build_love_bar(compatibility_score)

        # Create ship image
        heart_url = "https://cdn-icons-png.flaticon.com/512/833/833472.png"
        avatar_url1 = user1.display_avatar.url
        avatar_url2 = user2.display_avatar.url

        async with aiohttp.ClientSession() as session:
            async def fetch_image(url):
                async with session.get(url) as resp:
                    return await resp.read() if resp.status == 200 else None

            avatar_data1, avatar_data2, heart_data = await asyncio.gather(
                fetch_image(avatar_url1), fetch_image(avatar_url2), fetch_image(heart_url)
            )

        if not (avatar_data1 and avatar_data2 and heart_data):
            await ctx.send("⚠️ Unable to load one or more images. Try again later!")
            return

        # Create composite image
        avatar1 = self.create_circular_image(avatar_data1, size=(300, 300))
        avatar2 = self.create_circular_image(avatar_data2, size=(300, 300))
        heart_img = Image.open(io.BytesIO(heart_data)).convert("RGBA").resize((220, 220))

        canvas_width = 900
        canvas_height = 400
        composite = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))

        total_width = 300 + 220 + 300
        margin_x = (canvas_width - total_width) // 2
        avatar1_x = margin_x
        avatar1_y = (canvas_height - 300) // 2
        heart_x = avatar1_x + 300
        heart_y = (canvas_height - 220) // 2
        avatar2_x = heart_x + 220
        avatar2_y = (canvas_height - 300) // 2

        composite.paste(avatar1, (avatar1_x, avatar1_y), avatar1)
        composite.paste(heart_img, (heart_x, heart_y), heart_img)
        composite.paste(avatar2, (avatar2_x, avatar2_y), avatar2)

        buffer = io.BytesIO()
        composite.save(buffer, format="PNG")
        buffer.seek(0)

        love_quotes = [
            "Love is composed of a single soul inhabiting two bodies.",
            "The heart has its reasons which reason knows nothing of.",
            "Love recognizes no barriers. It jumps hurdles, leaps fences, penetrates walls."
        ]
        extra_quote = random.choice(love_quotes)

        # Dynamic embed color
        if compatibility_score >= 90:
            embed_color = discord.Color.from_rgb(255, 20, 147)
        elif compatibility_score >= 70:
            embed_color = discord.Color.from_rgb(255, 105, 180)
        elif compatibility_score >= 50:
            embed_color = discord.Color.from_rgb(219, 112, 147)
        elif compatibility_score >= 30:
            embed_color = discord.Color.from_rgb(176, 196, 222)
        else:
            embed_color = discord.Color.from_rgb(169, 169, 169)

        embed = discord.Embed(
            title=f"{heart_emoji}  Compatibility Result {'<a:RedHeart1:1360815733860470834>' if compatibility_score > 50 else '<:broken_heartpulse:1363882089262354482>'}",
            description=(
                f"**{user1.display_name}**  {'<a:RedHeart1:1360815733860470834>' if compatibility_score > 50 else '<:broken_heartpulse:1363882089262354482>'}  **{user2.display_name}**\\n\\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"{love_bar}\\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"*{message_comment}*\\n\\n"
                f"_{extra_quote}_"
            ),
            color=embed_color
        )

        embed.set_image(url="attachment://ship.png")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", 
                        icon_url=ctx.author.display_avatar.url)

        file = discord.File(fp=buffer, filename="ship.png")
        await ctx.send(embed=embed, file=file)

    @app_commands.command(name="poll", description="Create a quick poll.")
    async def poll_command(self, interaction: discord.Interaction, question: str, option1: str, option2: str):
        """Create a poll with two options."""
        await interaction.response.send_message("Your poll was created!", ephemeral=True)

        polls_channel = discord.utils.get(interaction.guild.channels, name="polls")
        if polls_channel is None:
            return

        embed = discord.Embed(
            title="New Poll",
            description=question,
            color=0xFFA500
        )
        embed.add_field(name="Option 1", value=option1, inline=False)
        embed.add_field(name="Option 2", value=option2, inline=False)
        embed.set_footer(text=f"Poll by {interaction.user.display_name}")

        poll_message = await polls_channel.send(embed=embed)
        await poll_message.add_reaction("1️⃣")
        await poll_message.add_reaction("2️⃣")

    def has_permission(self, user):
        """Check if user has permission to use certain commands."""
        if user.guild_permissions.administrator:
            return True
        allowed_roles = ["Staff", "Admin", "FunnyCommands", "Parliamentarian"]
        user_roles = [role.name for role in user.roles]
        return any(role in user_roles for role in allowed_roles)

    @commands.command(name="say")
    async def say(self, ctx, *, message: str = ""):
        """
        Repeat the user's message with optional attachments (images/files).
        Usage: ?say <message> [attach images/files]
        If no message is provided, it will send attached files only.
        """
        if not self.has_permission(ctx.author):
            return await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")

        files = []
        for attachment in ctx.message.attachments:
            if not hasattr(attachment, "filename") or not hasattr(attachment, "size"):
                await ctx.send("One of the attachments is missing or invalid.", delete_after=5)
                continue
            if attachment.size > 8 * 1024 * 1024:  # 8 MB limit
                await ctx.send(f"Attachment `{getattr(attachment, 'filename', 'unknown')}` is too large to upload (limit 8 MB).", delete_after=5)
                continue
            try:
                data = await attachment.read()
                discord_file = discord.File(io.BytesIO(data), filename=attachment.filename)
                files.append(discord_file)
            except discord.NotFound:
                await ctx.send(f"Attachment `{attachment.filename}` was not found or deleted.", delete_after=5)
            except discord.HTTPException:
                await ctx.send(f"Attachment `{attachment.filename}` was not found or deleted.", delete_after=5)
            except Exception as e:
                await ctx.send(f"Error reading `{getattr(attachment, 'filename', 'unknown')}`: {e}", delete_after=5)

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # Cannot delete message, ignore silently

        if not message and not files:
            await ctx.send("Nothing to say or upload.")
            return

        await ctx.send(content=message if message else None, files=files if files else None)
        
    @commands.command(name="replysay")
    async def replysay(self, ctx, *, message: str = ""):
        """
        Reply to a message on behalf of an admin.
        Usage: Reply to a message, then use ?replysay <message>
        """
        if not self.has_permission(ctx.author):
            return await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")

        if not ctx.message.reference or not ctx.message.reference.resolved:
            return await ctx.send("You must reply to a message to use this command.")

        target_message = ctx.message.reference.resolved
        files = []
        for attachment in ctx.message.attachments:
            if not hasattr(attachment, "filename") or not hasattr(attachment, "size"):
                continue
            if attachment.size > 8 * 1024 * 1024:
                continue
            try:
                data = await attachment.read()
                discord_file = discord.File(io.BytesIO(data), filename=attachment.filename)
                files.append(discord_file)
            except Exception:
                continue

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        await target_message.reply(content=message if message else None, files=files if files else None)

    @commands.command(name="bonk")
    async def bonk(self, ctx, member: discord.Member):
        """Bonk a user with a random bonk message and gif."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        bonk_gifs = [
            "https://tenor.com/view/bonk-doge-gif-24837098",
        ]
        bonk_msgs = [
            f"{ctx.author.mention} bonked {member.mention} for questionable behavior! <a:Bonk:1363639959957012623>",
            f"{ctx.author.mention} delivers a mighty BONK to {member.mention}! 🚨",
            f"{member.mention} got bonked by {ctx.author.mention}! Time to reflect!"
        ]
        await ctx.send(f"{random.choice(bonk_msgs)}\n{random.choice(bonk_gifs)}")

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member):
        """Send a kiss to a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        kiss_gifs = [
            "https://tenor.com/view/mocha-and-milk-gif-734972071031030497",
        ]
        kiss_msgs = [
            f"{ctx.author.mention} kissed {member.mention} <a:Kissy:1363640561826795630>",
            f"{ctx.author.mention} sends a sweet kiss to {member.mention}! 💋",
            f"{member.mention} received a loving kiss from {ctx.author.mention}!"
        ]
        await ctx.send(f"{random.choice(kiss_msgs)}\n{random.choice(kiss_gifs)}")

    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member):
        """Give a hug to a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        hug_gifs = [
            "https://tenor.com/view/theoffice-hug-gif-18038984",
        ]
        hug_msgs = [
            f"{ctx.author.mention} gave {member.mention} a big hug! <:Hug:1363641146571620495>",
            f"{ctx.author.mention} wraps {member.mention} in a warm hug! 🤗",
            f"{member.mention} is hugged tightly by {ctx.author.mention}!"
        ]
        await ctx.send(f"{random.choice(hug_msgs)}\n{random.choice(hug_gifs)}")

    @commands.command(name="slap")
    async def slap(self, ctx, member: discord.Member):
        """Slap a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        slap_gifs = [
            "https://tenor.com/view/peach-and-goma-peach-cat-goma-cat-peach-and-goma-cat-peach-cat-slap-gif-3790251090829977055",
        ]
        slap_msgs = [
            f"{ctx.author.mention} slapped {member.mention} <a:slaps:1363641570032619570>",
            f"{ctx.author.mention} delivers a dramatic slap to {member.mention}! 🖐️",
            f"{member.mention} got a surprise slap from {ctx.author.mention}!"
        ]
        await ctx.send(f"{random.choice(slap_msgs)}\n{random.choice(slap_gifs)}")

    @commands.command(name="yeet")
    async def yeet(self, ctx, member: discord.Member):
        """Yeet a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        yeet_gifs = [
            "https://tenor.com/view/yeet-trash-seal-dr-dolittle-dolittle-gif-15298225",
        ]
        yeet_msgs = [
            f"{ctx.author.mention} yeeted {member.mention} into the void! <a:Void:1363642029229215906>",
            f"{member.mention} was YEETED by {ctx.author.mention}! 🚀",
            f"{ctx.author.mention} launches {member.mention} with a powerful YEET!"
        ]
        await ctx.send(f"{random.choice(yeet_msgs)}\n{random.choice(yeet_gifs)}")

    @commands.command(name="facepalm")
    async def facepalm(self, ctx):
        """Express a facepalm with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        facepalm_gifs = [
            "https://media.tenor.com/3QvQKQwZpQwAAAAC/facepalm.gif",
            "https://media.tenor.com/6bQKQwZpQwAAAAC/anime-facepalm.gif"
        ]
        facepalm_msgs = [
            f"{ctx.author.mention} just facepalmed. <:FacePalm:1363642536354250844>",
            f"{ctx.author.mention} can't believe it... FACEPALM! 🤦",
            f"{ctx.author.mention} did a legendary facepalm!"
        ]
        await ctx.send(f"{random.choice(facepalm_msgs)}\n{random.choice(facepalm_gifs)}")

    @commands.command(name="rip")
    async def rip(self, ctx, member: discord.Member):
        """Declare a user as RIP with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        rip_gifs = [
            "https://tenor.com/view/dance-coffin-meme-rip-gif-16909625",
        ]
        rip_msgs = [
            f"{member.mention} has been officially declared **RIPPED** by {ctx.author.mention} <a:Cross:1363642688066420829>",
            f"{ctx.author.mention} pays respects to {member.mention}. F in chat.",
            f"{member.mention} has left the chat... RIP."
        ]
        await ctx.send(f"{random.choice(rip_msgs)}\n{random.choice(rip_gifs)}")

    @commands.command(name="kidnap")
    async def kidnap(self, ctx, member: discord.Member):
        """Kidnap a user for 1 hour with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        kidnap_gifs = [
            "https://tenor.com/view/kidnap-cat-kidnap-aaaaah-fear-horror-film-gif-21768777",
        ]
        kidnap_msgs = [
            f"{ctx.author.mention} has kidnapped {member.mention} for 1 hour! 🚐",
            f"{member.mention} was snatched by {ctx.author.mention}! Hide your snacks!",
            f"{ctx.author.mention} is taking {member.mention} on a mysterious adventure!"
        ]
        await ctx.send(f"{random.choice(kidnap_msgs)}\n{random.choice(kidnap_gifs)}")

    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member):
        """Kill a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        kill_gifs = [
            "https://tenor.com/view/stab-knife-kifluggs-kill-murder-gif-24765587",
        ]
        kill_msgs = [
            f"{ctx.author.mention} Killed {member.mention} <a:GhostFaceMurder:1363643010285441225>",
            f"{member.mention} was eliminated by {ctx.author.mention}! 💀",
            f"{ctx.author.mention} has sent {member.mention} to the shadow realm!"
        ]
        await ctx.send(f"{random.choice(kill_msgs)}\n{random.choice(kill_gifs)}")
        
    @commands.command(name="punch")
    async def punch(self, ctx, member: discord.Member):
        """Punch a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        punch_gifs = [
            "https://tenor.com/view/markiplier-markiplier-punch-markipler-funny-funny-punch-gif-23594121",
        ]
        punch_msgs = [
            f"{ctx.author.mention} punched {member.mention} <a:Peepo_Smash:1363886712606036179>",
            f"{member.mention} got a knockout punch from {ctx.author.mention}! 🥊",
            f"{ctx.author.mention} delivers a super punch to {member.mention}!"
        ]
        await ctx.send(f"{random.choice(punch_msgs)}\n{random.choice(punch_gifs)}")
    
    @commands.command(name="love")
    async def love(self, ctx, member: discord.Member):
        """Love a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        love_gifs = [
            "https://tenor.com/view/%EB%AA%A8%EC%B0%8C%EB%83%A5-gif-3199198135359664573",
        ]
        love_msgs = [
            f"{ctx.author.mention} loved {member.mention} <a:HailLeader:1363885731520446604>",
            f"{ctx.author.mention} sends love to {member.mention}! ❤️",
            f"{member.mention} is showered with love by {ctx.author.mention}!"
        ]
        await ctx.send(f"{random.choice(love_msgs)}\n{random.choice(love_gifs)}")
        
    @commands.command(name="dance")
    async def dance(self, ctx, member: discord.Member):
        """Dance with a user with a random gif and message."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return
        await ctx.message.delete()
        dance_gifs = [
            "https://tenor.com/view/johnny-english-johnny-english-movie-johnnyenglish-johnnyenglishmovie-rowan-gif-15226828216304945656",
        ]
        dance_msgs = [
            f"{ctx.author.mention} is dancing with {member.mention} <a:Anime_Dance:1363643358962253934>",
            f"{ctx.author.mention} and {member.mention} start a dance party! 💃🕺",
            f"{member.mention} joins {ctx.author.mention} for an epic dance-off!"
        ]
        await ctx.send(f"{random.choice(dance_msgs)}\n{random.choice(dance_gifs)}")

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member):
        """Show a user's avatar."""
        await ctx.send(f"{member.mention}'s avatar: {member.avatar.url}")
        
        if ctx.author.voice is None:
            await ctx.send("You must be in a voice channel to use this command.")
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        ydl_options = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": False,
            "extract_flat": False,
        }

        try:
            results = await search_ytdlp_async(url, ydl_options)
            if not results:
                await ctx.send("No results found for the provided URL.")
                return

            title = results.get("title", "Untitled")
            audio_url = results.get("url")
            thumbnail = results.get("thumbnail")
            duration = results.get("duration", 0)
            duration_formatted = f"{divmod(duration, 60)[0]:02d}:{divmod(duration, 60)[1]:02d}" if duration else "Unknown"

            # Determine service emoji based on URL
            service_emoji = "<:bot:1402928409897865288>"  # Default bot emoji
            if "youtube.com" in url.lower() or "youtu.be" in url.lower():
                service_emoji = "<:YouTubeMusic:1365325642647736443>"
            elif "spotify.com" in url.lower():
                service_emoji = "<:Spotify:1365325657306824774>"

            guild_id = str(ctx.guild.id)
            add_song_to_queue(guild_id, audio_url, title, ctx.author.name, thumbnail)

            if voice_client.is_playing() or voice_client.is_paused():
                embed = discord.Embed(
                    title=f"{service_emoji} Song Added to Queue",
                    color=0xF7B267
                )
                embed.set_author(
                    name="UnderLand Music",
                    icon_url="https://cdn-icons-png.flaticon.com/512/15585/15585721.png"
                )
                embed.add_field(name="Track", value=f"**{title}**", inline=False)
                embed.add_field(name="Requested By", value=ctx.author.mention, inline=True)
                embed.add_field(name="Duration", value=f"`{duration_formatted}`", inline=True)
                if thumbnail:
                    embed.set_thumbnail(url=thumbnail)
                embed.set_footer(text="NightZone • Next Up!")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"{service_emoji} Now Playing",
                    description=f"**{title}**\nDuration: `{duration_formatted}`",
                    color=0x1DB954
                )
                embed.set_thumbnail(url=thumbnail or discord.Embed.Empty)
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
                await play_next_song(voice_client, guild_id, ctx.channel)

        except Exception as e:
            await ctx.send(f"An error occurred while processing the URL: {e}")

    @commands.command(name="order55")
    async def order55(self, ctx):
        """Force the bot to leave ALL servers — OWNER ONLY."""
        OWNER_IDS = os.getenv("OWNER_IDS", "").split(",")
        if str(ctx.author.id) not in OWNER_IDS:
            await ctx.send("❌ You do not have permission to use this command.")
            return

        await ctx.send("⚠️ Executing Order 55... Leaving all servers.")
        for guild in self.bot.guilds:
            try:
                await guild.leave()
            except Exception as e:
                print(f"Failed to leave {guild.name} ({guild.id}): {e}")

    @commands.command(name="orderrole")
    @commands.has_role("Admin")
    async def orderrole(self, ctx, *, role_name: str):
        """Create a new server role (Admin only)."""
        guild = ctx.guild
        existing_role = discord.utils.get(guild.roles, name=role_name)
        if existing_role:
            await ctx.send(f"Role `{role_name}` already exists.")
            return
        try:
            await guild.create_role(name=role_name)
            await ctx.send(f"Role `{role_name}` created successfully.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to create roles.")
        except Exception as e:
            await ctx.send(f"Error creating role: {e}")

    @commands.command(name="associate")
    async def word_association(self, ctx, *, word: str):
        """Find related words for vocabulary building using Datamuse API (free)."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return

        try:
            async with aiohttp.ClientSession() as session:
                # Datamuse API - completely free, no API key needed
                url = f"https://api.datamuse.com/words"
                params = {
                    "ml": word,  # Words with similar meaning
                    "max": 10    # Limit to 10 results
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if not data:
                            await ctx.send(f"No related words found for **{word}**.")
                            return
                        
                        related_words = [item["word"] for item in data[:8]]  # Get top 8 words
                        
                        embed = discord.Embed(
                            title=f"🔗 Words Related to '{word.title()}'",
                            description=f"**Similar meaning:** {', '.join(related_words)}",
                            color=0x3498db
                        )
                        
                        # Also get rhyming words
                        rhyme_params = {"rel_rhy": word, "max": 5}
                        async with session.get(url, params=rhyme_params) as rhyme_response:
                            if rhyme_response.status == 200:
                                rhyme_data = await rhyme_response.json()
                                if rhyme_data:
                                    rhyming_words = [item["word"] for item in rhyme_data[:5]]
                                    embed.add_field(
                                        name="🎵 Rhymes",
                                        value=", ".join(rhyming_words),
                                        inline=False
                                    )
                        
                        embed.set_footer(text="💡 Great for vocabulary building and creative writing!")
                        await ctx.send(embed=embed)
                        
                    else:
                        await ctx.send("❌ Could not connect to the word association service.")
                        
        except Exception as e:
            await ctx.send(f"❌ Error fetching word associations: {e}")

    @commands.command(name="wiki")
    async def wikipedia_summary(self, ctx, *, topic: str):
        """Get Wikipedia summaries for learning topics using Wikipedia API (completely free)."""
        if not self.has_permission(ctx.author):
            await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
            return

        try:
            async with aiohttp.ClientSession() as session:
                # Wikipedia API - completely free, no API key needed
                search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_")
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        title = data.get("title", topic)
                        extract = data.get("extract", "No summary available.")
                        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                        thumbnail = data.get("thumbnail", {}).get("source", "")
                        
                        # Limit extract length for Discord
                        if len(extract) > 1000:
                            extract = extract[:997] + "..."
                        
                        embed = discord.Embed(
                            title=f"📚 {title}",
                            description=extract,
                            color=0x0066cc,
                            url=page_url
                        )
                        
                        if thumbnail:
                            embed.set_thumbnail(url=thumbnail)
                        
                        embed.add_field(
                            name="🔗 Learn More",
                            value=f"[Read full article on Wikipedia]({page_url})",
                            inline=False
                        )
                        
                        embed.set_footer(text="📖 Wikipedia • Great for learning and research!")
                        await ctx.send(embed=embed)
                        
                    elif response.status == 404:
                        # Try searching for the topic
                        search_api_url = "https://en.wikipedia.org/api/rest_v1/page/search"
                        params = {"q": topic, "limit": 1}
                        
                        async with session.get(search_api_url, params=params) as search_response:
                            if search_response.status == 200:
                                search_data = await search_response.json()
                                pages = search_data.get("pages", [])
                                
                                if pages:
                                    suggested_topic = pages[0]["title"]
                                    await ctx.send(f"❓ Topic not found. Did you mean: **{suggested_topic}**?\nTry: `?wiki {suggested_topic}`")
                                else:
                                    await ctx.send(f"❌ No Wikipedia article found for **{topic}**.")
                            else:
                                await ctx.send(f"❌ No Wikipedia article found for **{topic}**.")
                    else:
                        await ctx.send("❌ Could not connect to Wikipedia.")
                        
        except Exception as e:
            await ctx.send(f"❌ Error fetching Wikipedia summary: {e}")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(FunCog(bot))

    await bot.add_cog(FunCog(bot))



