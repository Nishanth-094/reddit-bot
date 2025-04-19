import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

# Load environment variables from the .env file
load_dotenv()

choices = {
    "✊": "rock",
    "✋": "paper",
    "✌️": "scissors"
}

class RPSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15)  # auto timeout after 15 seconds

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary, emoji="✊")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.success, emoji="✋")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.danger, emoji="✌️")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "scissors")

    async def play(self, interaction, player_choice):
        bot_choice = random.choice(list(choices.values()))
        
        if player_choice == bot_choice:
            result = "It's a tie!"
        elif (
            (player_choice == "rock" and bot_choice == "scissors") or
            (player_choice == "paper" and bot_choice == "rock") or
            (player_choice == "scissors" and bot_choice == "paper")
        ):
            result = "You win!"
        else:
            result = "I win!"

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"You chose **{player_choice}** {self.get_emoji(player_choice)}\n"
                    f"I chose **{bot_choice}** {self.get_emoji(bot_choice)}\n\n**{result}**",
            view=self
        )

    def get_emoji(self, choice):
        return next(emoji for emoji, name in choices.items() if name == choice)

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

@bot.command(name ='rps')
async def rps(ctx):
    view = RPSView()
    await ctx.send("Let's play Rock Paper Scissors! Choose your move:", view=view)


# Event when the bot successfully connects
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# Run the bot using the token
bot.run(TOKEN)