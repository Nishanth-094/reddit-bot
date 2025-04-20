import discord
from discord.ext import commands
import random
import asyncio
from main import SharedData

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
        
        if user_id not in SharedData.user_points:
            SharedData.user_points[user_id] = 0
            
        if player_choice == bot_choice:
            result = "It's a tie! (no points)"
        elif (
            (player_choice == "rock" and bot_choice == "scissors") or
            (player_choice == "paper" and bot_choice == "rock") or
            (player_choice == "scissors" and bot_choice == "paper")
        ):
            SharedData.user_points[user_id] += 7
            result = "You win! (+7 points)"
        else:
            SharedData.user_points[user_id] -= 3
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

class ChandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rps')
    async def rps(self, ctx):
        user_id = ctx.author.id
        # First send the introduction message without any view
        intro_msg = await ctx.send(f"{ctx.author.display_name}, we'll play 6 rounds of Rock Paper Scissors!")
        
        # Track user's total points at the start
        if str(user_id) not in SharedData.user_points:
            SharedData.user_points[str(user_id)] = 0
        starting_points = SharedData.user_points[str(user_id)]
        
        # Play 6 rounds
        for i in range(6):
            # Create a fresh view for each round
            view = RPSView(user_id)
            view.result_future = self.bot.loop.create_future()
            
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
        final_points = SharedData.user_points[str(user_id)]
        points_earned = final_points - starting_points
        
        # Send final message
        if points_earned > 0:
            await ctx.send(f"Game over! Wow, you actually played... You earned {points_earned} points, and now you have {final_points} points total. Could I *be*  any more impressed.")
        elif points_earned < 0:
            await ctx.send(f"Game over! Oh, look, you lost {abs(points_earned)} points. Now you're sitting at {final_points} points total. Could I *be*  any more disappointed?")
        else:
            await ctx.send(f"Game over! Wow, your points didn't change. You still have {final_points} points. Could I *be*  any more underwhelmed?")
            
        await ctx.send("As Joey sulks in his pizza, suddenly, the door bursts open. It's Phoebe!")
        await ctx.send("*\"Phoebe to Joey : Hey, I heard you got dumped again, Joey! Why do you keep doing that? It's like you're addicted to bad dates! But hey, maybe it's good for you – more time for pizza and singing songs about weird stuff!\"*")
        await ctx.send("*Phoebe spins around dramatically.*")
        await ctx.send("*\"Anyway, I've been working on something new. I think it could totally help you get over this! \"*")
        await ctx.send("*Phoebe pauses, almost as if she's waiting for something...*")
        await ctx.send("**Phoebe**: Alright, enough of the rambling! Think you can handle something totally not wierd? Just press `!pheebs` to give it a try!")

async def setup(bot):
    await bot.add_cog(ChandlerCog(bot))