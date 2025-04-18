import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

from wordle_game import get_random_word, get_feedback

active_games = {} 

# Load environment variables from the .env file
load_dotenv()

# Get the bot token from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")

# Create an instance of a bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member updates intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Sample NPC data
npc_data = {
    "npc1": {
        "name": "Milo",
        "greeting": ["Hello, traveler!", "Hey there!", "Greetings, adventurer!"],
        "status": "Milo is in good spirits, ready to help you."
    },
    "npc2": {
        "name": "Ariana",
        "greeting": ["Greetings!", "Hi!", "Welcome, adventurer!"],
        "status": "Ariana is feeling cautious today."
    }
}

# Command 1: !talk - Random greeting from an NPC
@bot.command(name='talk')
async def talk(ctx):
    npc = random.choice(list(npc_data.values()))
    greeting = random.choice(npc["greeting"])
    await ctx.send(f"{greeting} I am {npc['name']}.")

# Command 2: !npcstatus - Get the status of an NPC
@bot.command(name='npcstatus')
async def npcstatus(ctx):
    npc = random.choice(list(npc_data.values()))
    status = npc["status"]
    await ctx.send(f"{npc['name']} says: {status}")

# Event when the bot successfully connects
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")


@bot.command(name="wordle")
async def wordle(ctx):
    user_id = ctx.author.id
    if user_id in active_games:
        await ctx.send("You're already playing Wordle! Use `!guess yourword` to keep guessing.")
        return

    word = get_random_word()
    active_games[user_id] = {"word": word, "attempts": []}
    await ctx.send("🧠 Wordle started! Use `!guess yourword` to make a guess.")


@bot.command(name="guess")
async def guess(ctx, guess: str):
    user_id = ctx.author.id
    guess = guess.lower()

    if user_id not in active_games:
        await ctx.send("Start a game first using `!wordle`.")
        return

    if len(guess) != 5 or guess not in WORDS:  # You can replace this check with a full dictionary
        await ctx.send("Invalid guess. Make sure it's a valid 5-letter word.")
        return

    game = active_games[user_id]
    feedback = get_feedback(game["word"], guess)
    game["attempts"].append((guess, feedback))

    board = "\n".join(f"{g.upper()} {f}" for g, f in game["attempts"])
    await ctx.send(f"```\n{board}\n```")

    if guess == game["word"]:
        await ctx.send(f"🎉 Correct! You guessed the word in {len(game['attempts'])} tries.")
        del active_games[user_id]
    elif len(game["attempts"]) >= 6:
        await ctx.send(f"❌ Out of tries! The word was **{game['word'].upper()}**.")
        del active_games[user_id]



# Run the bot using the token
bot.run(TOKEN)
