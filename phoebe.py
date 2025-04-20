import discord
from discord.ext import commands
import random
import asyncio
import os
from main import SharedData

class PhoebeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='pheebs')
    async def phoebe(self, ctx):
        user_id = str(ctx.author.id)
        # Ensure game state exists
        if user_id not in SharedData.phoebe_games:
            SharedData.phoebe_games[user_id] = {"active": True, "guessed": False}
        else:
            SharedData.phoebe_games[user_id]["active"] = True
            SharedData.phoebe_games[user_id]["guessed"] = False
            
        # Ensure user has a points entry
        if user_id not in SharedData.user_points:
            SharedData.user_points[user_id] = 0
            
        # Check if the image file exists
        image_path = "/Users/brindap/Documents/git/discord-bot_1/images/smelly_cat.jpeg"
        if not os.path.exists(image_path):
            await ctx.send("Oops! Phoebe can't find her picture! (Image file not found)")
            SharedData.phoebe_games[user_id]['active'] = False
            return
            
        file = discord.File(image_path, filename="smelly_cat.jpeg")
        embed = discord.Embed(title="Phoebe's Mystery Image")
        embed.set_image(url="attachment://smelly_cat.jpeg")
        embed.description = "**Phoebe**: I wrote a song about this! Can you guess what it is?"
        await ctx.send(file=file, embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
            
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            guess = msg.content.lower()
            
            if "smelly cat" in guess:
                SharedData.phoebe_games[user_id]["guessed"] = True
                SharedData.phoebe_games[user_id]["active"] = False
                responses = [
                    "Oh my God, you got it! You must be psychic too!🎵 Smelly cat, smelly cat, what are they feeding you? 🎵",
                    "That's right! 🎵 Smelly cat, smelly cat, what are they feeding you? 🎵",
                    "Yes! I wrote that after a cat followed me home. It was REALLY smelly.🎵 Smelly cat, smelly cat, what are they feeding you? 🎵",
                    "Wow! It's like we share the same brain! That's exactly right!🎵 Smelly cat, smelly cat, what are they feeding you? 🎵"
                ]
                SharedData.user_points[user_id] += 10
                await ctx.send(f"**Phoebe**: {random.choice(responses)} (+10 points! Total: {SharedData.user_points[user_id]} points)")
            elif "cat" in guess:
                SharedData.phoebe_games[user_id]["active"] = False
                responses = [
                    "Ooh, so close! It's like you're almost reading my aura!",
                    "You're on the right track! The cat is definitely involved, but it has a... certain quality.",
                    "Cat is right! But this cat has a very distinctive... um... fragrance issue.",
                    "Oh! You're like, halfway there! This cat has a very specific odor problem."
                ]
                SharedData.user_points[user_id] += 3
                await ctx.send(f"**Phoebe**: {random.choice(responses)} (+3 points! Total: {SharedData.user_points[user_id]} points)")
                await ctx.send("**Phoebe**: 🎵 Smelly cat, smelly cat, what are they feeding you? 🎵")
            else:
                SharedData.phoebe_games[user_id]["active"] = False
                responses = [
                    "No, no, no! But that's okay, the universe works in mysterious ways.",
                    "That's not it, but that could be my next song!",
                    "Hmm, not what I was thinking, but I like your creativity!",
                    "Oh, sweetie, no. But I appreciate your vibes!"
                ]
                await ctx.send(f"**Phoebe**: {random.choice(responses)}")
                await ctx.send("**Phoebe**: It was 'Smelly Cat'! 🎵 Smelly cat, smelly cat, what are they feeding you? 🎵")
        except asyncio.TimeoutError:
            SharedData.phoebe_games[user_id]["active"] = False
            await ctx.send("**Phoebe**: Oh! You got distracted by the spirits too? I was waiting for your guess!")
            await ctx.send("**Phoebe**: It was 'Smelly Cat'! 🎵 Smelly cat, smelly cat, what are they feeding you? 🎵")

        audio_file = '/Users/brindap/Documents/git/friends_bot/audio/smelly_cat.mp3' 

        if ctx.author.voice:
            channel = ctx.author.voice.channel
            # Connect to the voice channel
            voice_channel = await channel.connect()
            # Play the audio
            voice_channel.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: print('done', e))
            # Wait until the audio finishes before disconnecting
            while voice_channel.is_playing():
                await asyncio.sleep(1)
            # Disconnect after playback
            await voice_channel.disconnect()
        else:
            # This message should be sent only if the user isn't in a voice channel
            await ctx.send("Join a voice channel so you can suffer from Phoebe's singing!")

            
        await ctx.send("Phoebe smiles at you, still singing, but suddenly, the door bursts open.")
        await ctx.send(f"Suddenly, Ross bursts through the door, holding a *Dinosaur book* in his hand.")
        await ctx.send(f"**Ross**: *Okay, so, I was doing some more research, and I found this completely new species of dinosaur...*")
        await ctx.send("**Phoebe**: Ross, don't start with your dino talk. No one wants to hear about 'T. rex in love' again.")
        await ctx.send("**Ross**: Fineeee.... Oh hey have you heard of the game *Wordle*? It's, like, totally about figuring out words with, uh, clues and stuff... Type `!wordle` if you wanna give it a shot")

    @commands.command(name='phoebe')
    async def phoebe_quote(self, ctx):
        """Get a random Phoebe quote"""
        quotes = [
            "Oh, I wish I could, but I don't want to.",
            "They don't know that we know they know we know!",
            "Something is wrong with the left phalange!",
            "I need to go, because I'm not sure I can be around this beautiful food.",
            "It's like a cow's opinion. It just doesn't matter. It's moo.",
            "I'm very bendy!",
            "See? He's her lobster!",
            "Oh, you like that? You should hear my phone number!",
            "I don't even have a 'pla'!",
            "Okay, but if I'm too harsh, you need to stop me because once I start, I just can't stop."
        ]
        await ctx.send(f"**Phoebe**: {random.choice(quotes)}")

async def setup(bot):
    await bot.add_cog(PhoebeCog(bot))