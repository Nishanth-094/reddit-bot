import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import asyncio
from typing import Dict, List

# Load environment variables from the .env file
load_dotenv()
# Get the bot token from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")

# Create an instance of a bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Joey's data (from Friends)
npc_data = {
    "name": "Joey Tribbiani",
    "greeting": [
        "How *you* doin'?",
        "Hey, it's Joey!",
        "Sup? Joey's here!"
    ],
    "status": "Joey just had a meatball sub and is feelin' great.",
    "favorites": ["pizza", "meatball sub", "sandwich", "jacket", "food", "cologne"]
}

# Track user points and unlocked characters
user_points = {}
unlocked_characters = {}

# !talk
@bot.command(name='talk')
async def talk(ctx):
    greeting = random.choice(npc_data["greeting"])
    await ctx.send(f"{greeting} I am {npc_data['name']}.")

# !gift
@bot.command(name='gift')
async def gift(ctx, *, item: str):
    user_id = str(ctx.author.id)
    favorites = npc_data["favorites"]
    item = item.lower()
    
    if user_id not in user_points:
        user_points[user_id] = 0
    
    if item in favorites:
        user_points[user_id] += 5
        await ctx.send(f"Okay, hear me out... if you keep this up, I might actually share my sandwich with you. Maybe.\" (+5 points)")
    else:
        user_points[user_id] -= 3
        responses = [
            f"Joey looks at the {item} and says, \"Uh... does it come with fries?\" (-3 points)",
            f"\"What am I supposed to do with a {item}? Wear it? Eat it?\" Joey squints. (-3 points)",
            f"Joey frowns. \"This ain't food. Do you *know* me at all?\" (-3 points)",
            f"Joey holds it up. \"So... you're sayin' this is *better* than a sandwich?\" (-3 points)"
        ]
        await ctx.send(random.choice(responses))

# !joeyline
@bot.command(name='joeyline')
async def joeyline(ctx):
    lines = [
        "How *you* doin'?",
        "Joey doesn't share food!",
        "It's not that common, it *doesn't* happen to every guy, and it *is* a big deal!",
        "If he doesn't like you, this is all a moo point... it's like a cow's opinion, it doesn't matter. It's moo."
    ]
    await ctx.send(random.choice(lines))

# !joeytrivia
@bot.command(name='joeytrivia')
async def joey_trivia(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_points:
        user_points[user_id] = 0
    
    if user_id not in unlocked_characters:
        unlocked_characters[user_id] = []
    
    question = "Joey just got ghosted. Again. What's for dinner?"
    options = [
        "A) Self-pity and soup",
        "B) Leftovers",
        "C) Pizza",
        "D) Chandler's emotional support lasagna"
    ]
    correct_answer = "c"
    
    await ctx.send(f"{question}\n" + "\n".join(options))
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for("message", check=check, timeout=30.0)
        user_answer = msg.content.lower()
        
        if user_answer == correct_answer:
            user_points[user_id] += 5
            await ctx.send("✅ Correct! Pizza never ghosts. 🍕 (+5 points)")
        else:
            user_points[user_id] -= 2
            await ctx.send("❌ Wrong! Joey's disappointed. (-2 points)")
        
        # Send the Joey reaction image
        try:
            file = discord.File("images/joey_mad.jpeg", filename="joey_mad.jpeg")
            embed = discord.Embed(title="Joey's Reaction")
            embed.set_image(url="attachment://joey_mad.jpeg")
            await ctx.send(file=file, embed=embed)
        except FileNotFoundError:
            await ctx.send("Joey would show you his reaction, but the image file is missing!")
        
        if "chandler" not in unlocked_characters[user_id]:
            unlocked_characters[user_id].append("chandler")
            await ctx.send("🎉 *Chandler appears anyway... because pizza.*")
        else:
            await ctx.send("🍕 Chandler reappears... again... with sarcasm.")
        
        if user_answer == correct_answer:
            await ctx.send("Chandler shows up holding a pizza and says:\n*\"Could I *be carrying any more toppings?\"** 😂")
        else:
            await ctx.send("Chandler walks in, looks at Joey, and says:\n*\"You missed pizza? Who *are you right now?\"** 😅")
        
        await ctx.send(f"{ctx.author.display_name}, you now have {user_points[user_id]} points.")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to answer! Joey got bored and ate all the pizza.")

# !points
@bot.command(name='points')
async def check_points(ctx):
    user_id = str(ctx.author.id)
    points = user_points.get(user_id, 0)
    await ctx.send(f"{ctx.author.display_name}, you have {points} points.")

# Define RPS choices globally
choices = {
    "✊": "rock",
    "✋": "paper",
    "✌️": "scissors"
}

class RPSButton(discord.ui.Button):
    def __init__(self, label, emoji, style, custom_id):
        super().__init__(label=label, emoji=emoji, style=style, custom_id=custom_id)
        
    async def callback(self, interaction):
        await self.view.play(interaction, self.custom_id)

class RPSView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=15)
        self.user_id = user_id
        self.result_future = None
        
        # Add buttons
        self.add_item(RPSButton(
            label="Rock", 
            emoji="✊", 
            style=discord.ButtonStyle.primary, 
            custom_id="rock"
        ))
        self.add_item(RPSButton(
            label="Paper", 
            emoji="✋", 
            style=discord.ButtonStyle.success, 
            custom_id="paper"
        ))
        self.add_item(RPSButton(
            label="Scissors", 
            emoji="✌️", 
            style=discord.ButtonStyle.danger, 
            custom_id="scissors"
        ))

    async def interaction_check(self, interaction):
        return interaction.user.id == self.user_id
        
    async def play(self, interaction, player_choice):
        bot_choice = random.choice(list(choices.values()))
        user_id = str(interaction.user.id)
        
        if user_id not in user_points:
            user_points[user_id] = 0
            
        if player_choice == bot_choice:
            result = "It's a tie! (no points)"
        elif (
            (player_choice == "rock" and bot_choice == "scissors") or
            (player_choice == "paper" and bot_choice == "rock") or
            (player_choice == "scissors" and bot_choice == "paper")
        ):
            user_points[user_id] += 7
            result = "You win! (+7 points)"
        else:
            user_points[user_id] -= 3
            result = "You lose! (-3 points)"
            
        # Disable all buttons
        for child in self.children:
            child.disabled = True
            
        await interaction.response.edit_message(
            content=f"You chose **{player_choice}** {self.get_emoji(player_choice)}\n"
                   f"I chose **{bot_choice}** {self.get_emoji(bot_choice)}\n\n**{result}**",
            view=self
        )
        
        if self.result_future and not self.result_future.done():
            self.result_future.set_result(True)
    
    def get_emoji(self, choice):
        return next(emoji for emoji, name in choices.items() if name == choice)
    
    async def on_timeout(self):
        if self.result_future and not self.result_future.done():
            self.result_future.set_exception(asyncio.TimeoutError())

@bot.command(name='rps')
async def rps(ctx):
    user_id = ctx.author.id
    # First send the introduction message without any view
    intro_msg = await ctx.send(f"{ctx.author.display_name}, we'll play 6 rounds of Rock Paper Scissors!")
    
    # Track user's total points at the start
    if str(user_id) not in user_points:
        user_points[str(user_id)] = 0
    starting_points = user_points[str(user_id)]
    
    # Play 6 rounds
    for i in range(6):
        # Create a fresh view for each round
        view = RPSView(user_id)
        view.result_future = bot.loop.create_future()
        
        # Send the round message with the view
        msg = await ctx.send(f"**Round {i+1}**: Choose your move:", view=view)
        
        try:
            # Wait for the player to make a choice
            await asyncio.wait_for(view.result_future, timeout=15.0)
        except asyncio.TimeoutError:
            # Handle timeout - disable buttons and show timeout message
            for child in view.children:
                child.disabled = True
            await msg.edit(content=f"**Round {i+1}**: ⏰ You took too long! Skipping this round.", view=view)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    
    # Calculate points earned during the game
    final_points = user_points[str(user_id)]
    points_earned = final_points - starting_points
    
    # Send final message
    if points_earned > 0:
        await ctx.send(f"Game over! You earned {points_earned} points and now have {final_points} points total.")
    elif points_earned < 0:
        await ctx.send(f"Game over! You lost {abs(points_earned)} points and now have {final_points} points total.")
    else:
        await ctx.send(f"Game over! Your points didn't change. You still have {final_points} points.")

# Global error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Try !help to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument provided.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        print(f"Unhandled error: {error}")

WORD_LIST = [
    "house", "table", "chair", "apple", "basic",
    "cloud", "dance", "flute", "grape", "image"
]

class WordleGame:
    def __init__(self):
        self.word = random.choice(WORD_LIST)
        self.guesses: List[str] = []
        self.max_attempts = 6
        self.completed = False

    def make_guess(self, guess: str) -> Dict[int, str]:
        if len(guess) != 5:
            raise ValueError("Guess must be 5 letters long")
        
        if not guess.isalpha():
            raise ValueError("Guess must contain only letters")
            
        if len(self.guesses) >= self.max_attempts:
            raise ValueError("No more attempts remaining")
        
        guess = guess.lower()
        
        # Don't add duplicate guesses
        if guess not in self.guesses:
            self.guesses.append(guess)
        
        result = {}
        for i, letter in enumerate(guess):
            if letter == self.word[i]:
                result[i] = "green"  # Correct position
            elif letter in self.word:
                result[i] = "yellow"  # Correct letter, wrong position
            else:
                result[i] = "gray"  # Incorrect letter
        
        if guess == self.word:
            self.completed = True
            
        return result

    def evaluate_guess(self, guess: str) -> Dict[int, str]:
        """Evaluate a guess without adding it to the guesses list"""
        result = {}
        for i, letter in enumerate(guess):
            if letter == self.word[i]:
                result[i] = "green"
            elif letter in self.word:
                result[i] = "yellow"
            else:
                result[i] = "gray"
        return result

    def get_visual_state(self) -> str:
        if not self.guesses:
            return "No guesses yet!"
        
        output = []
        for guess in self.guesses:
            # Use evaluate_guess instead of make_guess
            result = self.evaluate_guess(guess)
            row = ""
            for i, letter in enumerate(guess):
                color = result[i]
                if color == "green":
                    row += f"🟩 "
                elif color == "yellow":
                    row += f"🟨 "
                else:
                    row += f"⬜ "
            output.append(row)
        
        # Add attempts remaining
        attempts_left = self.max_attempts - len(self.guesses)
        output.append(f"\nAttempts remaining: {attempts_left}/6")
        
        return "\n".join(output)
    
# Game state storage
wordle_games: Dict[int, WordleGame] = {}

@bot.command(name='wordle')
async def wordle(ctx):
    user_id = ctx.author.id
    
    if user_id in wordle_games and not wordle_games[user_id].completed:
        await ctx.send("You already have an active game! Use !guess <word> to make a guess.")
        return
    
    wordle_games[user_id] = WordleGame()
    await ctx.send(f"New Wordle game started! Use !guess <word> to make a guess.\nYou have 6 attempts to guess a 5-letter word.")

@bot.command(name='guess')
async def guess(ctx, word: str):
    user_id = ctx.author.id
    
    if user_id not in wordle_games:
        await ctx.send("No active game! Start a new game with !wordle")
        return
    
    game = wordle_games[user_id]
    
    try:
        result = game.make_guess(word)
        visual = game.get_visual_state()
        
        if game.completed:
            if word.lower() == game.word:
                await ctx.send(f"🎉 Congratulations! You won!\n{visual}")
            else:
                await ctx.send(f"Game Over! The word was **{game.word}**\n{visual}")
            del wordle_games[user_id]
        else:
            await ctx.send(visual)
        
    except ValueError as e:
        await ctx.send(f"❌ {str(e)}")

# on_ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    print("------")

# Run the bot
bot.run(TOKEN)