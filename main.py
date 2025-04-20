import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from the .env file
load_dotenv()

# Get the bot token from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")

# Create an instance of a bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Shared data dictionaries that will be accessible to all cogs
class SharedData:
    user_points = {}
    unlocked_characters = {}
    phoebe_games = {}
    wordle_games = {}

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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    print("------")

# Load all cogs
async def load_extensions():
    await bot.load_extension("joey")
    await bot.load_extension("chandler")
    await bot.load_extension("phoebe")
    await bot.load_extension("ross")

# Run the bot
async def main():
    try:
        # Load opus for voice functionality
        discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')
    except Exception as e:
        print(f"Error loading opus: {e}")
        print("Voice functionality may not work properly.")
    
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())