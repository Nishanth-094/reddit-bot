import discord
from discord.ext import commands
import random
from typing import Dict, List
from main import SharedData
import os

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
                result[i] = "green" # Correct position
            elif letter in self.word:
                result[i] = "yellow" # Correct letter, wrong position
            else:
                result[i] = "gray" # Incorrect letter
                
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

class RossCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wordle')
    async def wordle(self, ctx):
        user_id = ctx.author.id
        if user_id in SharedData.wordle_games and not SharedData.wordle_games[user_id].completed:
            await ctx.send("You already have an active game! Use !guess <word> to make a guess.")
            return
            
        SharedData.wordle_games[user_id] = WordleGame()
        await ctx.send(f"New Wordle game started! Use !guess <word> to make a guess.\nYou have 6 attempts to guess a 5-letter word.")

    @commands.command(name='guess')
    async def guess(self, ctx, word: str):
        user_id = ctx.author.id
        if user_id not in SharedData.wordle_games:
            await ctx.send("No active game! Start a new game with !wordle")
            return
        
        game = SharedData.wordle_games[user_id]
        try:
            result = game.make_guess(word)
            visual = game.get_visual_state()
            
            # Check if the game is over (either won or all attempts used)
            game_over = game.completed or len(game.guesses) >= game.max_attempts
            
            if game_over:
                if game.completed:
                    await ctx.send(f"🎉 Congratulations! You won!\n{visual}")
                    await ctx.send("**Rachel Enters**")
                    await ctx.send("*Hey! What are you doing spending time with these losers*")
                    image_path = "/Users/brindap/Documents/git/friends_bot/images/congrats.jpeg"
                    if not os.path.exists(image_path):
                        await ctx.send("Oops! Rachel can't find her picture! (Image file not found)")
                        if 'phoebe_games' in SharedData.__dict__ and user_id in SharedData.phoebe_games:
                            SharedData.phoebe_games[user_id]['active'] = False
                        return
                    file = discord.File(image_path, filename="congrats.jpeg")
                    embed = discord.Embed(title="")
                    embed.set_image(url="attachment://congrats.jpeg")
                    await ctx.send(file=file, embed=embed)
                    await ctx.send("Umm... HELLO?! Somebody's killing it today! Congrats, superstar!")
                else:
                    await ctx.send(f"Game Over! The word was **{game.word}**\n{visual}")
                    await ctx.send("**Rachel Enters**")
                    await ctx.send("*Hey! What are you doing spending time with these losers*")
                    image_path = "/Users/brindap/Documents/git/friends_bot/images/loser.jpg"
                    if not os.path.exists(image_path):
                        await ctx.send("Oops! Rachel can't find her picture! (Image file not found)")
                        if 'phoebe_games' in SharedData.__dict__ and user_id in SharedData.phoebe_games:
                            SharedData.phoebe_games[user_id]['active'] = False
                        return
                    file = discord.File(image_path, filename="loser.jpg")
                    embed = discord.Embed(title="")
                    embed.set_image(url="attachment://loser.jpg")
                    await ctx.send(file=file, embed=embed)
                    await ctx.send("Aww... better luck next time, sweetie. And maybe try not losing?")
                
                # Clean up the game
                del SharedData.wordle_games[user_id]
            else:
                await ctx.send(visual)
        except ValueError as e:
            await ctx.send(f"❌ {str(e)}")
            
async def setup(bot):
    await bot.add_cog(RossCog(bot))