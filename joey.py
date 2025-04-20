import discord
from discord.ext import commands
import random
import asyncio
import os
from main import SharedData

# NPC Data (Joey)
npc_data = {
    "name": "Joey Tribbiani",
    "status": "Joey just had a meatball sub and is feelin' great.",
    "favorites": ["pizza", "meatball sub", "sandwich", "jacket", "food", "cologne"]
}

# Audio file path
audio_file = '/Users/brindap/Documents/git/friends_bot/audio/Joey - Hey, How You Doin_.mp3'

class JoeyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='talk')
    async def talk(self, ctx):
        greeting = "Hey, how *you* doin'?"
        # Check if the user is in a voice channel
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
            await ctx.send("Join a voice channel so Joey can talk to you!")
        await ctx.send("Hey! Do you wanna hear about my day today? It might not the best one, but hey, it's Joey we're talkin' about!. Type press `!tell_story`, and I will spill the beans!")

    @commands.command(name='gift')
    async def gift(self, ctx, *, item: str):
        user_id = str(ctx.author.id)
        favorites = npc_data["favorites"]
        item = item.lower()
        
        if user_id not in SharedData.user_points:
            SharedData.user_points[user_id] = 0
            
        if item in favorites:
            SharedData.user_points[user_id] += 5
            await ctx.send(f"Okay, hear me out... if you keep this up, I might actually share my sandwich with you. Maybe.\" (+5 points)")
        else:
            SharedData.user_points[user_id] -= 3
            responses = [
                f"Joey looks at the {item} and says, \"Uh... does it come with fries?\" (-3 points)",
                f"\"What am I supposed to do with a {item}? Wear it? Eat it?\" Joey squints. (-3 points)",
                f"Joey frowns. \"This ain't food. Do you *know* me at all?\" (-3 points)",
                f"Joey holds it up. \"So... you're sayin' this is *better* than a sandwich?\" (-3 points)"
            ]
            await ctx.send(random.choice(responses))

    @commands.command(name='joeyline')
    async def joeyline(self, ctx):
        lines = [
            "Joey doesn't share food!",
            "It's not that common, it *doesn't* happen to every guy, and it *is* a big deal!",
            "If he doesn't like you, this is all a moo point... it's like a cow's opinion, it doesn't matter. It's moo."
        ]
        await ctx.send(random.choice(lines))

    @commands.command(name='tell_story')
    async def joey_trivia(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in SharedData.user_points:
            SharedData.user_points[user_id] = 0
        if user_id not in SharedData.unlocked_characters:
            SharedData.unlocked_characters[user_id] = []
            
        await ctx.send("Joey : So, I was on a date, right? I go, 'Hey, how you doin'?' She dumps me! ")
        question = "Joey just got ghosted. Again. What's for dinner?"
        options = [
            "A) Self-pity and soup",
            "B) Leftovers",
            "C) Pizza and more pizza",
            "D) Chandler's emotional support lasagna"
        ]
        correct_answer = "🇨"
        question_message = await ctx.send(f"{question}\n" + "\n".join(options))
        
        # Add reaction options to the message
        reactions = ["🇦", "🇧", "🇨", "🇩"]
        for reaction in reactions:
            await question_message.add_reaction(reaction)
            
        def check(reaction, user):
            return user != self.bot.user and reaction.message.id == question_message.id and str(reaction.emoji) in reactions
            
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30.0)
            user_answer = str(reaction.emoji).lower()
            
            if user_answer == correct_answer:
                SharedData.user_points[user_id] += 5
                await ctx.send("✅ Correct! Pizza never ghosts. 🍕 (+5 points)")
            else:
                SharedData.user_points[user_id] -= 2
                await ctx.send("❌ Wrong! Joey's disappointed. (-2 points)")
                
            # Send the Joey reaction image
            try:
                file = discord.File("images/joey_mad.jpeg", filename="joey_mad.jpeg")
                embed = discord.Embed(title="Joey's Reaction")
                embed.set_image(url="attachment://joey_mad.jpeg")
                await ctx.send(file=file, embed=embed)
            except FileNotFoundError:
                await ctx.send("Joey would show you his reaction, but the image file is missing!")
                
            if "chandler" not in SharedData.unlocked_characters[user_id]:
                SharedData.unlocked_characters[user_id].append("chandler")
                await ctx.send("🎉 *Chandler appears ... because pizza.*")
            else:
                await ctx.send("🍕 Chandler appears... ... with pizza topped with sarcasm.")
                
            if user_answer == correct_answer:
                await ctx.send("Chandler shows up holding a pizza and says:\n \"*Could I be carrying any more toppings?*\" 😂")
            else:
                await ctx.send("Chandler walks in, looks at Joey, and says:\n\"*You missed pizza? Well, let me just bring in another one... because that's what friends do*\" 😅")
                
            await ctx.send(f"{ctx.author.display_name}, you now have {SharedData.user_points[user_id]} points.")
            
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer! Joey got bored and ate all the pizza.")
            await ctx.send("Chandler walks in, looks at Joey, and says:\n\"*You missed pizza? Well, let me just bring in another one... because that's what friends do*\" 😅")

        await ctx.send("Chandler strolls in, looks at Joey, and says:\n\"*You know what, Joey? Just eat the pizza. I'll deal with you later. Anyway, if anyone is up for a game, type `!rps` and let's see who wins this time.*\" 🍕✋✊✌️")

    @commands.command(name='points')
    async def check_points(self, ctx):
        user_id = str(ctx.author.id)
        points = SharedData.user_points.get(user_id, 0)
        await ctx.send(f"{ctx.author.display_name}, you have {points} points.")

async def setup(bot):
    await bot.add_cog(JoeyCog(bot))