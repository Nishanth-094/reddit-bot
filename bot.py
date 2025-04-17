import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

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

# Run the bot using the token
bot.run(TOKEN)
