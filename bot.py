# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import asyncio
import sys
import traceback # Keep for logging unexpected errors

load_dotenv()

# --- Bot Setup ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True # Needs to be enabled in Developer Portal!
intents.guilds = True
# Consider adding intents.reactions if you add reaction-based features later

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=commands.DefaultHelpCommand( # Add a basic help command
        no_category = 'Game Commands'
    )
)

# --- Game States ---
# Tic Tac Toe
ongoing_tictactoe_games = {}
# Structure: {user_id: {'channel': ctx.channel, 'board': [...], 'player': 'X' or 'O', 'bot_player': 'O' or 'X', 'difficulty': 'easy'/'hard', 'message': <last_board_message>, 'intro_message': <intro_msg_object>}}
user_tictactoe_scores = {} # Persistent scores
bot_tictactoe_score = 0

# Murder Mystery
ongoing_murder_games = {}
# Structure: {user_id: {'channel': ctx.channel, 'suspects': [], 'murderer': '', 'clues_given': 0, 'stage': 'asking_clues/guessing', 'clue_indices': []}}

# Math Puzzle
ongoing_math_games = {}
# Structure: {user_id: {'channel': ctx.channel, 'score': 0, 'questions_asked': 0, 'current_answer': None, 'current_task': None, 'difficulty': 'easy'/'hard', 'total_questions': 0}}


# --- Murder Mystery Game Data ---
SUSPECTS = ["Professor Plum", "Miss Scarlett", "Colonel Mustard"]
CLUES = [
    ("Someone with muddy boots was seen near the library.", "Imagine a picture of muddy footprints.", "Colonel Mustard"),
    ("A faint scent of expensive perfume lingered in the hallway.", "Imagine a picture of a fancy perfume bottle.", "Miss Scarlett"),
    ("A complex scientific equation was scribbled on a napkin nearby.", "Imagine a picture of mathematical formulas.", "Professor Plum"),
    ("The victim was arguing about rare books earlier.", "Imagine a picture of old books.", "Professor Plum"),
    ("A single red rose was found near the scene, its stem snapped.", "Imagine a picture of a broken red rose.", "Miss Scarlett"),
    ("Witnesses heard talk of strategy and old battles.", "Imagine a picture of chess pieces or maps.", "Colonel Mustard"),
]

# --- Math Puzzle Game Data ---
MATH_OPERATIONS = ['+', '-', '*', '/']
MAX_NUMBER_EASY = 15
MAX_NUMBER_HARD = 50
TIME_LIMIT_EASY_MATH = 15
TIME_LIMIT_HARD_MATH = 8
QUESTIONS_EASY_MATH = 7
QUESTIONS_HARD_MATH = 7
POINTS_EASY_MATH = 1
POINTS_HARD_MATH = 2


# --- Helper Functions ---
def check_user_message(original_author, original_channel):
    """Returns a check function for wait_for that verifies message author and channel."""
    def inner_check(message):
        # Ignore bot's own messages and ensure correct user/channel
        return message.author == original_author and message.channel == original_channel and not message.author.bot
    return inner_check

# --- Tic Tac Toe Game Logic ---

def create_ttt_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def display_ttt_board(board):
    board_str = "```\n"
    board_str += "  0 | 1 | 2 \n"
    board_str += " ---+---+---\n"
    for i, row in enumerate(board):
        # Ensure cell content is treated as string, handle None or other types safely
        row_str = [str(c) if c is not None else ' ' for c in row]
        board_str += f"{i} | {' | '.join(row_str)}\n"
        if i < 2:
            board_str += " ---+---+---\n"
    board_str += "```"
    return board_str

def is_valid_ttt_move(board, row, col):
    # Check bounds first to prevent IndexError
    if not (0 <= row < 3 and 0 <= col < 3):
        return False
    # Then check if the cell is empty
    return board[row][col] == ' '

def make_ttt_move(board, row, col, player):
    if is_valid_ttt_move(board, row, col):
        board[row][col] = player
        return True
    return False

def check_ttt_win(board, player):
    n = 3
    # Check rows
    if any(all(board[r][c] == player for c in range(n)) for r in range(n)): return True
    # Check columns
    if any(all(board[r][c] == player for r in range(n)) for c in range(n)): return True
    # Check main diagonal (top-left to bottom-right)
    if all(board[i][i] == player for i in range(n)): return True
    # Check anti-diagonal (top-right to bottom-left)
    if all(board[i][n - 1 - i] == player for i in range(n)): return True
    return False

def check_ttt_draw(board):
    return all(board[r][c] != ' ' for r in range(3) for c in range(3))

def get_empty_cells(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ' ']

# --- TTT AI Logic ---
def get_ttt_ai_move_easy(board):
    available_moves = get_empty_cells(board)
    return random.choice(available_moves) if available_moves else None

def get_ttt_ai_move_hard(board, bot_player):
    opponent_player = 'X' if bot_player == 'O' else 'O'
    empty_cells = get_empty_cells(board)
    if not empty_cells: # Should not happen if called correctly, but safety check
        return None

    # 1. Check for winning move
    for r, c in empty_cells:
        temp_board = [row[:] for row in board] # Create a copy
        temp_board[r][c] = bot_player
        if check_ttt_win(temp_board, bot_player):
             # print(f"AI ({bot_player}): Found winning move at {r},{c}") # Debugging
             return (r, c)

    # 2. Check for blocking move
    for r, c in empty_cells:
        temp_board = [row[:] for row in board] # Create a copy
        temp_board[r][c] = opponent_player
        if check_ttt_win(temp_board, opponent_player):
            # print(f"AI ({bot_player}): Found blocking move at {r},{c}") # Debugging
            return (r, c)

    # 3. Try Center
    if board[1][1] == ' ':
        # print(f"AI ({bot_player}): Taking center {1},{1}") # Debugging
        return (1, 1)

    # 4. Try Opposite Corner (if opponent is in a corner)
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    for r, c in corners:
        if board[r][c] == opponent_player:
            opposite_r, opposite_c = 2 - r, 2 - c
            if board[opposite_r][opposite_c] == ' ':
                # print(f"AI ({bot_player}): Taking opposite corner {opposite_r},{opposite_c}") # Debugging
                return (opposite_r, opposite_c)

    # 5. Try Empty Corner
    empty_corners = [pos for pos in corners if board[pos[0]][pos[1]] == ' ']
    if empty_corners:
        move = random.choice(empty_corners) # Choose a random empty corner
        # print(f"AI ({bot_player}): Taking empty corner {move[0]},{move[1]}") # Debugging
        return move

    # 6. Try Empty Side
    sides = [(0, 1), (1, 0), (1, 2), (2, 1)]
    empty_sides = [pos for pos in sides if board[pos[0]][pos[1]] == ' ']
    if empty_sides:
        move = random.choice(empty_sides) # Choose a random empty side
        # print(f"AI ({bot_player}): Taking empty side {move[0]},{move[1]}") # Debugging
        return move

    # 7. Fallback (should theoretically not be reached if logic above is sound and empty_cells exist)
    # print(f"AI ({bot_player}): Fallback - picking random from {empty_cells}") # Debugging
    return random.choice(empty_cells) # Should always have a move if board isn't full

# --- Scoring Logic ---
def update_ttt_scores(user_id, outcome, difficulty):
    global user_tictactoe_scores, bot_tictactoe_score
    user_score = user_tictactoe_scores.get(user_id, 0)
    # Define points based on difficulty
    points_win_easy, points_lose_easy = 1, -1 # Easy: +1 for win, -1 for loss
    points_win_hard, points_lose_hard = 3, -1 # Hard: +3 for win, -1 for loss

    if difficulty == 'easy':
        points_win, points_lose = points_win_easy, points_lose_easy
    else: # hard
        points_win, points_lose = points_win_hard, points_lose_hard

    if outcome == 'user_win':
        user_score += points_win
        bot_tictactoe_score += points_lose # Bot loses points when user wins
    elif outcome == 'bot_win':
        user_score += points_lose # User loses points when bot wins
        bot_tictactoe_score += points_win
    # Draw outcome doesn't change scores in this setup

    user_tictactoe_scores[user_id] = user_score
    # Ensure bot score doesn't go below 0, perhaps? (Optional)
    # bot_tictactoe_score = max(0, bot_tictactoe_score)
    return user_score, bot_tictactoe_score


# --- Discord Bot Events ---

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print(f'Discord.py Version: {discord.__version__}')
    print('Bot is ready and online!')
    print('------')
    await bot.change_presence(activity=discord.Game(name="!ttt | !guess | !math | !help"))

@bot.event
async def on_command_error(ctx, error):
    # Ignore CommandNotFound silently
    if isinstance(error, commands.CommandNotFound):
        # print(f"Command not found: {ctx.message.content}") # Optional: Log for debugging
        return # Or send a very brief message: await ctx.send("?", delete_after=5)

    # Handle specific, common errors first
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ You don't have permission to use the `{ctx.command.name}` command.")
    elif isinstance(error, commands.BotMissingPermissions):
        # Extract missing permissions list if available
        missing_perms = getattr(error, 'missing_permissions', getattr(error, 'missing_perms', None))
        if missing_perms:
             await ctx.send(f"❌ I don't have the required permissions (`{', '.join(missing_perms)}`) to run the `{ctx.command.name}` command here.")
        else:
             await ctx.send(f"❌ I don't have the required permissions to run the `{ctx.command.name}` command here.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Slow down! Try `!{ctx.command.name}` again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"🤔 Missing argument: `{error.param.name}`. Use `!help {ctx.command.name}` for usage.")
    elif isinstance(error, commands.UserInputError): # Broader category for bad input (like BadArgument)
        await ctx.send(f"⚠️ Invalid input for `!{ctx.command.name}`. Check `!help {ctx.command.name}`.")
    elif isinstance(error, commands.CheckFailure):
        # This catches our custom is_user_in_game check and others (like has_permissions inside a check)
        # Provide a slightly more informative message if possible
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("🚫 This command cannot be used in private messages.")
        # Add checks for other specific CheckFailures if you implement them
        else:
            await ctx.send("🚫 You cannot run this command right now (perhaps you're in another game, in DMs, or don't meet criteria?).")
    # Handle Discord API errors potentially raised from checks/commands
    elif isinstance(error, discord.Forbidden):
        # This often relates to permissions but can occur outside specific command checks
        await ctx.send(f"🔐 I lack the necessary Discord permissions to perform an action required by the `{ctx.command.name}` command (Error Code: {error.code}). Check my role permissions.")
    elif isinstance(error, discord.NotFound):
         # 404 errors - typically when trying to act on a message/user/channel that no longer exists
        await ctx.send(f"❓ Something went missing (like a message, user, or channel - Error Code: {error.code}). Please try the command again.")
    elif isinstance(error, discord.HTTPException):
         # Catch other network/API related errors from Discord
        await ctx.send(f"🌐 A network error occurred while communicating with Discord (Status: {error.status}, Code: {error.code}). Please try again later.")

    # Log unexpected errors and notify user
    else:
        # This catches errors not handled above
        print(f'!!! Unhandled exception in command {ctx.command}:', file=sys.stderr)
        # Get the original error if it's wrapped in CommandInvokeError
        original_error = getattr(error, 'original', error)
        traceback.print_exception(type(original_error), original_error, original_error.__traceback__, file=sys.stderr)
        try:
             await ctx.send("💥 An unexpected error occurred! I've logged the details for the developer.")
        except discord.Forbidden:
             print("!!! Bot lacks permission to send error message in channel.", file=sys.stderr)


# --- Check if user is in any game ---
def is_user_in_game(user_id):
    """Checks if a user ID is present in any of the ongoing game dictionaries."""
    return user_id in ongoing_tictactoe_games or \
           user_id in ongoing_murder_games or \
           user_id in ongoing_math_games

# Custom check function for commands decorator
def check_not_in_game():
    async def predicate(ctx):
        if is_user_in_game(ctx.author.id):
            await ctx.send("🚫 You are already in a game! Finish or stop your current game first.", delete_after=15)
            return False
        return True
    return commands.check(predicate)

# --- Murder Mystery Game Command ---

@bot.command(name='guess', aliases=['murder', 'mystery'], help="Starts a 'Guess the Murderer' game.")
@commands.cooldown(1, 30, commands.BucketType.user)
@check_not_in_game() # Use the custom check
async def guess_murderer(ctx):
    user_id = ctx.author.id
    # Ensure we have enough unique suspects and clues
    if len(SUSPECTS) < 3 or len(CLUES) < 3:
         await ctx.send("⚠️ Game configuration error: Not enough suspects or clues defined.")
         return

    chosen_suspects = random.sample(SUSPECTS, 3)
    murderer = random.choice(chosen_suspects)
    # Get indices for all clues, shuffle them, and take the first 3
    all_clue_indices = list(range(len(CLUES)))
    random.shuffle(all_clue_indices)
    chosen_clue_indices = all_clue_indices[:3]

    game_state = {
        'channel': ctx.channel,
        'suspects': chosen_suspects,
        'murderer': murderer,
        'clues_given': 0,
        'stage': 'asking_clues',
        'clue_indices': chosen_clue_indices # Store the chosen indices
    }
    ongoing_murder_games[user_id] = game_state

    await ctx.send(f"A murder has occurred! 🕵️\nThe suspects are: **{', '.join(chosen_suspects)}**.")
    await asyncio.sleep(1)
    await ctx.send("I will give you 3 clues...")
    await asyncio.sleep(2)

    max_clues = 3
    while game_state['clues_given'] < max_clues:
        # Check if game was stopped externally (e.g., by a !stop command if implemented)
        if user_id not in ongoing_murder_games:
             print(f"Murder mystery game for {user_id} stopped prematurely.")
             return

        current_clue_index = game_state['clue_indices'][game_state['clues_given']]
        clue_text, clue_image_desc, _ = CLUES[current_clue_index] # Hint/answer part not shown directly

        embed = discord.Embed(title=f"Clue #{game_state['clues_given'] + 1}", description=clue_text, color=discord.Color.blue())
        embed.set_footer(text=f"Visual Hint: {clue_image_desc}") # Use footer for the 'visual' part
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
             await ctx.send("⚠️ I lack permission to send embeds in this channel. Cannot proceed with clues.")
             del ongoing_murder_games[user_id]
             return
        except discord.HTTPException as e:
              await ctx.send(f"⚠️ Network error sending clue ({e.status}). Stopping game.")
              del ongoing_murder_games[user_id]
              return

        game_state['clues_given'] += 1

        # Wait between clues, unless it's the last clue
        if game_state['clues_given'] < max_clues:
            await asyncio.sleep(10) # Wait time between clues
        else:
             await asyncio.sleep(1) # Shorter pause after the last clue
             await ctx.send("That's all the clues! Time to make your accusation.")

    # Final check if game still exists before prompting for accusation
    if user_id not in ongoing_murder_games:
        print(f"Murder mystery game for {user_id} ended before accusation stage.")
        return

    ongoing_murder_games[user_id]['stage'] = 'guessing'
    # Pick a random suspect for the example command usage
    example_suspect = random.choice(chosen_suspects)
    await ctx.send(f"Who is the murderer? Use `!accuse Name` (e.g., `!accuse \"{example_suspect}\"`)")

@bot.command(name='accuse', help="Accuse a suspect in the Murder Mystery game.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def accuse(ctx, *, suspect_name: str):
    user_id = ctx.author.id
    if user_id not in ongoing_murder_games:
        await ctx.send("You're not currently investigating a murder. Start one with `!guess`.")
        return

    game_state = ongoing_murder_games[user_id]
    if game_state['stage'] != 'guessing':
        await ctx.send("You need to receive all the clues before you can accuse someone!")
        return

    # Normalize the input and the correct answer for comparison
    normalized_guess = suspect_name.strip().title() # Capitalize words for better matching
    correct_murderer = game_state['murderer']

    # Find the suspect matching the guess, ignoring case and using title case for comparison
    # This is slightly more robust than just lower() if names have multiple caps
    found_match = next((s for s in game_state['suspects'] if normalized_guess.lower() == s.lower()), None)


    if not found_match:
        # Provide the list of valid suspects again
        await ctx.send(f"'{suspect_name}' is not one of the current suspects. The suspects are: {', '.join(game_state['suspects'])}. Please try again.")
        return

    # Now compare the found match (with original casing) to the correct murderer
    if found_match == correct_murderer:
        await ctx.send(f"🎉 **Correct!** **{correct_murderer}** was the murderer! Case closed!")
    else:
        await ctx.send(f"❌ **Incorrect!** It wasn't {found_match}. The real murderer was **{correct_murderer}**. Better luck next time!")

    # End the game by removing the state
    del ongoing_murder_games[user_id]

# --- Math Puzzle Game Command ---

def generate_math_problem(level='easy'):
    """Generates a math problem string and its answer based on difficulty."""
    num1, num2 = 0, 0
    op = '+'
    max_num = MAX_NUMBER_EASY if level == 'easy' else MAX_NUMBER_HARD

    if level == 'easy':
        op = random.choice(['+', '-', '*'])
        if op == '+':
            num1 = random.randint(1, max_num)
            num2 = random.randint(1, max_num)
        elif op == '-':
            # Ensure result is non-negative for easy
            num1 = random.randint(1, max_num)
            num2 = random.randint(0, num1) # num2 <= num1
        elif op == '*':
            # Keep numbers smaller for multiplication in easy
            num1 = random.randint(1, int(max_num**0.5) + 1)
            num2 = random.randint(1, max_num // num1 if num1 != 0 else max_num)

    else: # hard
        op = random.choice(MATH_OPERATIONS)
        if op == '+':
            num1 = random.randint(1, max_num)
            num2 = random.randint(1, max_num)
        elif op == '-':
            # Allow negative results
            num1 = random.randint(-max_num // 2, max_num)
            num2 = random.randint(-max_num // 2, max_num)
        elif op == '*':
            num1 = random.randint(-max_num // 2, max_num // 2)
            num2 = random.randint(-max_num // 2, max_num // 2)
            # Avoid 0*0 maybe?
            if num1 == 0 and num2 == 0: num1 = random.randint(1, 5)
        elif op == '/':
             # Ensure division results in an integer or reasonably simple float
             # Generate divisor first, then make num1 a multiple
             divisor = random.randint(1, max_num // 3) # Smaller divisors are common
             multiple = random.randint(-max_num // divisor, max_num // divisor)
             num1 = divisor * multiple
             num2 = divisor

    # Construct question string
    # Handle negative numbers in subtraction/addition more cleanly
    if op in ['+', '-'] and num2 < 0:
         question = f"{num1} {op} ({num2})" # Add parenthesis for clarity
    else:
         question = f"{num1} {op} {num2}"

    try:
        # Use eval carefully only on self-generated strings from safe components
        answer = eval(f"{num1}{op}{num2}") # More direct eval
        # Round floats to 2 decimal places, convert whole floats to int
        if isinstance(answer, float):
            if answer.is_integer():
                answer = int(answer)
            else:
                answer = round(answer, 2)
    except ZeroDivisionError:
        # Should be rare with the generation logic, but recurse if it happens
        # print("Warning: ZeroDivisionError encountered, regenerating math problem.")
        return generate_math_problem(level)
    except Exception as e:
         # Catch other potential eval errors
         print(f"Error evaluating math problem '{question}': {e}")
         return generate_math_problem(level) # Regenerate on error

    return f"What is {question}?", answer

@bot.command(name='math', aliases=['mathpuzzle'], help="Starts a timed math quiz (easy/hard). Usage: !math")
@commands.cooldown(1, 20, commands.BucketType.user)
@check_not_in_game()
async def math_puzzle(ctx):
    user_id = ctx.author.id
    await ctx.send("Choose difficulty: `easy` or `hard`?")
    try:
        # Wait for user's difficulty choice
        difficulty_msg = await bot.wait_for('message', check=check_user_message(ctx.author, ctx.channel), timeout=30.0)
        difficulty = difficulty_msg.content.strip().lower()
        if difficulty not in ['easy', 'hard']:
            await ctx.send("Invalid difficulty. Please type `easy` or `hard`. Aborting math puzzle.")
            return
        # Attempt to delete the user's difficulty message (best effort)
        try: await difficulty_msg.delete()
        except (discord.Forbidden, discord.NotFound): pass

    except asyncio.TimeoutError:
        await ctx.send("You didn't choose a difficulty in time. Aborting math puzzle.")
        return

    # Set game parameters based on difficulty
    questions_total = QUESTIONS_EASY_MATH if difficulty == 'easy' else QUESTIONS_HARD_MATH
    time_limit = TIME_LIMIT_EASY_MATH if difficulty == 'easy' else TIME_LIMIT_HARD_MATH
    points_per_q = POINTS_EASY_MATH if difficulty == 'easy' else POINTS_HARD_MATH
    max_score = questions_total * points_per_q

    await ctx.send(f"Starting **{difficulty.upper()}** Math Puzzle! 🧮\n{questions_total} questions, {time_limit} seconds per question.")
    # Initialize game state for the user
    game_state = {
        'channel': ctx.channel, 'score': 0, 'questions_asked': 0,
        'current_answer': None, 'current_task': None, 'difficulty': difficulty,
        'total_questions': questions_total
    }
    ongoing_math_games[user_id] = game_state

    # --- Question Loop ---
    while game_state['questions_asked'] < game_state['total_questions']:
        # Check if the game was stopped externally (e.g., !stopmath)
        if user_id not in ongoing_math_games:
             print(f"Math game for {user_id} stopped during question loop.")
             return

        question, answer = generate_math_problem(game_state['difficulty'])
        game_state['current_answer'] = answer
        game_state['questions_asked'] += 1

        # Create and send the question embed
        embed_color = discord.Color.green() if difficulty == 'easy' else discord.Color.orange()
        embed = discord.Embed(
            title=f"Question {game_state['questions_asked']}/{game_state['total_questions']} ({difficulty.title()})",
            description=f"**{question}**", # Make question bold
            color=embed_color
        )
        embed.set_footer(text=f"You have {time_limit} seconds to answer.")
        q_message = None
        try:
            q_message = await ctx.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException) as e:
             await ctx.send(f"⚠️ Error sending question embed ({e}). Stopping game.")
             if user_id in ongoing_math_games: del ongoing_math_games[user_id]
             return

        # --- Wait for Answer ---
        try:
            # Start waiting for the user's message
            # Use asyncio.create_task to allow cancellation by !stopmath
            msg_task = asyncio.create_task(
                bot.wait_for('message', check=check_user_message(ctx.author, ctx.channel), timeout=time_limit)
            )
            game_state['current_task'] = msg_task
            user_msg = await msg_task
            # If we get here, the user responded in time

            # Check game state again *after* wait_for returns, in case !stopmath was used
            if user_id not in ongoing_math_games:
                print(f"Math game for {user_id} stopped after user answered but before processing.")
                return

            # Process the answer
            try:
                user_answer_str = user_msg.content.strip().replace(',', '') # Handle potential commas
                # Try converting to float first for flexibility with decimals
                user_answer = float(user_answer_str)
                # Convert to int if it's numerically equivalent to an integer
                if user_answer == int(user_answer):
                    user_answer = int(user_answer)

                correct_answer = game_state['current_answer']

                # Comparison logic: use approximate comparison for floats
                is_correct = False
                # Check types for safe comparison
                if isinstance(correct_answer, float) or isinstance(user_answer, float):
                    try:
                        # Use abs difference for float comparison
                        is_correct = abs(float(user_answer) - float(correct_answer)) < 0.01
                    except TypeError:
                         is_correct = False # Cannot compare types
                else: # Assume integer comparison otherwise
                    is_correct = (user_answer == correct_answer)


                if is_correct:
                    game_state['score'] += points_per_q
                    feedback_msg = f"✅ Correct! Your score: {game_state['score']}"
                else:
                    feedback_msg = f"❌ Incorrect. The answer was {correct_answer}. Your score: {game_state['score']}"
                await ctx.send(feedback_msg, delete_after=7)

            except ValueError:
                # Handle cases where input isn't a valid number
                await ctx.send(f"⚠️ That wasn't a valid number. The answer was {game_state['current_answer']}. Score: {game_state['score']}", delete_after=7)
            finally:
                 # Attempt to delete the user's answer message (best effort)
                 try: await user_msg.delete()
                 except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass

        except asyncio.TimeoutError:
            # Check game state again on timeout
            if user_id not in ongoing_math_games:
                 print(f"Math game for {user_id} stopped during timeout.")
                 return
            # User ran out of time
            await ctx.send(f"⏰ Time's up! The answer was {game_state['current_answer']}. Score: {game_state['score']}", delete_after=7)
            # Task is already cancelled/finished due to timeout
            game_state['current_task'] = None # Clear the task reference

        except asyncio.CancelledError:
             # This happens if !stopmath cancels the task
             print(f"Math game for {user_id} was cancelled (likely by !stopmath).")
             # Game state should have been deleted by !stopmath, so just return
             return

        finally:
            # Ensure task reference is cleared if it exists
            if user_id in ongoing_math_games:
                 ongoing_math_games[user_id]['current_task'] = None
                 ongoing_math_games[user_id]['current_answer'] = None # Clear answer after processing

            # Attempt to delete the question embed after a short delay (best effort)
            if q_message: # Check if message was sent successfully
                await asyncio.sleep(1.5) # Give feedback message time to show
                try: await q_message.delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass


        # Pause before the next question, if the game hasn't ended
        if user_id in ongoing_math_games and game_state['questions_asked'] < game_state['total_questions']:
             await asyncio.sleep(1.5)

    # --- Game End ---
    # Check if the game state still exists (it might have been deleted by !stopmath)
    if user_id in ongoing_math_games:
        final_score = ongoing_math_games[user_id]['score']
        final_difficulty = ongoing_math_games[user_id]['difficulty']
        # Calculate max score again based on final difficulty state
        final_points_per_q = POINTS_EASY_MATH if final_difficulty == 'easy' else POINTS_HARD_MATH
        final_total_questions = QUESTIONS_EASY_MATH if final_difficulty == 'easy' else QUESTIONS_HARD_MATH
        final_max_score = final_total_questions * final_points_per_q

        await ctx.send(f"🏁 Math Puzzle ({final_difficulty.upper()}) finished!\nYour final score: **{final_score}/{final_max_score}** points.")
        # Clean up the game state
        del ongoing_math_games[user_id]

@bot.command(name='stopmath', help="Stops your current math puzzle game.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def stop_math_puzzle(ctx):
    user_id = ctx.author.id
    if user_id in ongoing_math_games:
        game_state = ongoing_math_games[user_id]
        # Cancel the wait_for task if it's active and hasn't finished
        wait_task = game_state.get('current_task')
        if wait_task and not wait_task.done():
            wait_task.cancel() # Cancel the asyncio task waiting for user input
            # print(f"Cancelled math wait_for task for {user_id}") # Debugging
        # Delete game state immediately after cancelling task (or if no task was running)
        del ongoing_math_games[user_id]
        await ctx.send("Math puzzle stopped.")
    else:
        await ctx.send("You are not currently playing a math puzzle.")


# --- Tic Tac Toe Command ---

@bot.command(name='tictactoe', aliases=['ttt'], help="Play Tic Tac Toe vs AI (easy/hard). Usage: !ttt")
@commands.cooldown(1, 15, commands.BucketType.user)
@check_not_in_game()
async def tictactoe(ctx):
    user_id = ctx.author.id
    await ctx.send("Choose difficulty: `easy` or `hard`?")
    try:
        difficulty_msg = await bot.wait_for('message', check=check_user_message(ctx.author, ctx.channel), timeout=30.0)
        difficulty = difficulty_msg.content.strip().lower()
        if difficulty not in ['easy', 'hard']:
            await ctx.send("Invalid difficulty. Use `easy` or `hard`. Aborting Tic Tac Toe.")
            return
        # Try deleting difficulty choice message (best effort)
        try: await difficulty_msg.delete()
        except (discord.NotFound, discord.Forbidden): pass
    except asyncio.TimeoutError:
        await ctx.send("No difficulty chosen in time. Aborting Tic Tac Toe.")
        return

    # Initialize game state
    game_state = {
        'channel': ctx.channel,
        'board': create_ttt_board(),
        'player': 'X', # User always starts as X
        'bot_player': 'O',
        'difficulty': difficulty,
        'message': None, # Stores the discord.Message object for the board
        'intro_message': None # Stores the initial "Starting game..." message
    }
    ongoing_tictactoe_games[user_id] = game_state

    # Send initial messages and store them in game_state
    try:
        intro_msg = await ctx.send(f"Starting **{difficulty.upper()}** Tic Tac Toe! You are 'X', I am 'O'.")
        game_state['intro_message'] = intro_msg # Store intro message
        board_message_content = display_ttt_board(game_state['board']) + "\nYour turn ('X'). Enter move `row,col` (e.g. `1,1`) or `!stopttt`"
        board_msg_object = await ctx.send(board_message_content)
        game_state['message'] = board_msg_object # Store the board message object
    except (discord.Forbidden, discord.HTTPException) as e:
        await ctx.send(f"⚠️ Error sending initial game messages ({e}). Cannot start game.")
        if user_id in ongoing_tictactoe_games: del ongoing_tictactoe_games[user_id] # Clean up state
        return

    # --- Game Loop ---
    outcome = None # Track game outcome: 'user_win', 'bot_win', 'draw', 'stopped'
    final_message = "" # Message to display at the end

    while True:
        # Check if game was stopped externally (e.g., !stopttt) before proceeding
        if user_id not in ongoing_tictactoe_games:
            print(f"TTT game for {user_id} stopped during loop.")
            return # Exit if game state was deleted

        # Get current game details from state
        game_state = ongoing_tictactoe_games[user_id]
        board = game_state['board']
        current_player_symbol = game_state['player']
        bot_player_symbol = game_state['bot_player']
        difficulty_level = game_state['difficulty']
        board_msg = game_state['message'] # The discord.Message object for the board

        # Ensure board_msg exists before trying to use it
        if not board_msg:
             await ctx.send("⚠️ Error: Board message reference lost. Stopping game.")
             outcome = 'stopped'
             final_message = "Game stopped due to internal error."
             break

        # --- USER'S TURN (X) ---
        if current_player_symbol == 'X':
            try:
                # Wait for the user's move message
                user_move_msg = await bot.wait_for('message', check=check_user_message(ctx.author, ctx.channel), timeout=60.0)
                content = user_move_msg.content.strip().lower()

                # Check for stop command first
                if content == '!stopttt':
                    # Call the dedicated stop command function to handle cleanup
                    await stop_tictactoe(ctx) # This will delete the game state and send messages
                    return # Exit the tictactoe command function immediately

                # --- Process Move Input ---
                try:
                    # Attempt to parse "row,col" format
                    row, col = map(int, content.split(','))
                except (ValueError, IndexError):
                    await ctx.send("Invalid format. Use `row,col` (e.g., `1,2`) or `!stopttt`.", delete_after=10)
                    # Try deleting the invalid message (best effort)
                    try: await user_move_msg.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass
                    continue # Ask for input again without switching turn

                # --- Validate and Make Move ---
                # Check game state again *after* wait_for, before making move
                if user_id not in ongoing_tictactoe_games: return

                if make_ttt_move(board, row, col, current_player_symbol):
                    # Move was valid and made
                    # Update Board Message to show the move and indicate bot's turn
                    try:
                        await board_msg.edit(content=display_ttt_board(board) + f"\nMy turn ({bot_player_symbol})... 🤔")
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                        await ctx.send(f"⚠️ Error updating board message ({e}). Stopping game.")
                        outcome = 'stopped'
                        final_message = "Game stopped due to message update error."
                        break # Exit game loop

                    # --- Delete User Move Message (Best Effort) ---
                    try: await user_move_msg.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass

                    # --- Check Game End Conditions AFTER user's move ---
                    if check_ttt_win(board, current_player_symbol):
                        outcome = 'user_win'
                        final_message = f"🎉 You won against the **{difficulty_level.upper()}** AI, {ctx.author.display_name}!"
                        break # Exit loop
                    elif check_ttt_draw(board):
                        outcome = 'draw'
                        final_message = "😐 It's a draw!"
                        break # Exit loop
                    else:
                        # If game continues, switch turn to bot
                        if user_id in ongoing_tictactoe_games: # Check state before modifying
                             ongoing_tictactoe_games[user_id]['player'] = bot_player_symbol
                else:
                    # Move was invalid (cell taken or out of bounds)
                    await ctx.send("Invalid move (cell occupied or out of bounds). Try again.", delete_after=10)
                    # Try deleting the invalid message (best effort)
                    try: await user_move_msg.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass
                    continue # Ask for input again without switching turn

            except asyncio.TimeoutError:
                # Check state again on timeout
                if user_id not in ongoing_tictactoe_games: return
                # User ran out of time
                outcome = 'bot_win' # Bot wins by default if user times out
                final_message = f"⏰ Time's up! The **{difficulty_level.upper()}** AI wins by default."
                break # Exit loop

        # --- BOT'S TURN (O) ---
        elif current_player_symbol == bot_player_symbol:
            # Bot "thinking" time
            await asyncio.sleep(random.uniform(0.7, 1.5))
            # Check if game was stopped during sleep
            if user_id not in ongoing_tictactoe_games: return

            # --- Get Bot Move ---
            move_func = get_ttt_ai_move_easy if difficulty_level == 'easy' else get_ttt_ai_move_hard
            # Pass bot's symbol to hard AI function
            bot_move = move_func(board) if difficulty_level == 'easy' else move_func(board, bot_player_symbol)

            if bot_move and make_ttt_move(board, bot_move[0], bot_move[1], current_player_symbol):
                # Bot move was valid and made
                 # Update Board Message to show bot's move and indicate user's turn
                try:
                    await board_msg.edit(content=display_ttt_board(board) + "\nYour turn ('X'). Enter `row,col` or `!stopttt`.")
                except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                    await ctx.send(f"⚠️ Error updating board message after bot move ({e}). Stopping game.")
                    outcome = 'stopped'
                    final_message = "Game stopped due to message update error."
                    break # Exit game loop

                # --- Check Game End Conditions AFTER bot's move ---
                if check_ttt_win(board, current_player_symbol):
                    outcome = 'bot_win'
                    final_message = f"🤖 The **{difficulty_level.upper()}** AI wins!"
                    break # Exit loop
                elif check_ttt_draw(board):
                    outcome = 'draw'
                    final_message = "😐 It's a draw!"
                    break # Exit loop
                else:
                    # If game continues, switch turn to user
                    if user_id in ongoing_tictactoe_games: # Check state before modifying
                         ongoing_tictactoe_games[user_id]['player'] = 'X'
            else:
                # Bot failed to move - should only happen if board is full but draw wasn't detected?
                # Or if AI function returns None unexpectedly
                print(f"!!! TTT Bot ({difficulty_level}) failed to find/make a valid move for {user_id} on board:\n{display_ttt_board(board)}")
                # Check if it's actually a draw that wasn't caught
                if check_ttt_draw(board):
                     outcome = 'draw'
                     final_message = "😐 It looks like a draw!"
                else: # Unexpected failure
                     outcome = 'stopped' # Treat as an error/stopped game
                     final_message = "🤔 Hmm, I got stuck somehow! Stopping the game."
                break # Exit loop

    # --- Game Over Sequence ---
    # This block only runs if the loop exited via 'break' (win, draw, error)
    # If the game was stopped by !stopttt, the function would have returned earlier.
    if user_id in ongoing_tictactoe_games:
        # Get final details before deleting state
        final_difficulty = ongoing_tictactoe_games[user_id]['difficulty']
        board_msg_obj = ongoing_tictactoe_games[user_id].get('message')
        intro_msg_obj = ongoing_tictactoe_games[user_id].get('intro_message')
        final_board_state = ongoing_tictactoe_games[user_id]['board'] # Capture final board

        # Update scores if the game ended normally (win/loss)
        score_message = ""
        if outcome in ['user_win', 'bot_win']:
            user_score, bot_score_updated = update_ttt_scores(user_id, outcome, final_difficulty)
            score_message = f"\nScores updated ({final_difficulty.title()}): You: {user_score} | Bot: {bot_tictactoe_score}"
        elif outcome == 'draw':
             user_score = user_tictactoe_scores.get(user_id, 0)
             score_message = f"\nScores unchanged: You: {user_score} | Bot: {bot_tictactoe_score}"


        # Try to update the final board message with the outcome
        if board_msg_obj:
            try:
                # Display final board state and the outcome message
                await board_msg_obj.edit(content=display_ttt_board(final_board_state) + f"\n**{final_message}**{score_message}")
            except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                print(f"Warning: Failed to edit final board message: {e}")
                # If edit fails, send the final message and scores separately
                await ctx.send(f"**{final_message}**{score_message}")
        else:
            # If board message object was lost, send final message anyway
             await ctx.send(f"**{final_message}**{score_message}")

        # Try to delete the initial "Starting game..." message (best effort)
        if intro_msg_obj:
             try: await intro_msg_obj.delete(delay=10) # Delay deletion slightly
             except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass

        # Clean up game state *after* processing results
        del ongoing_tictactoe_games[user_id]

    # If user_id was already removed (e.g., by !stopttt), the loop would have exited via return,
    # and this game over sequence wouldn't run.


@bot.command(name='stopttt', aliases=['stoptictactoe', 'quitttt'], help="Quits your current Tic Tac Toe game.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def stop_tictactoe(ctx):
    user_id = ctx.author.id
    if user_id in ongoing_tictactoe_games:
        # Retrieve message objects before deleting state
        board_msg_obj = ongoing_tictactoe_games[user_id].get('message')
        intro_msg_obj = ongoing_tictactoe_games[user_id].get('intro_message')

        # Delete state first to prevent race conditions in the main game loop
        del ongoing_tictactoe_games[user_id]
        await ctx.send("Tic Tac Toe game stopped.") # Confirm stop to user

        # Try to cleanup messages (best effort)
        if board_msg_obj:
            try:
                await board_msg_obj.edit(content="```\nGame Stopped by User.\n```", delete_after=15)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass # Ignore errors on cleanup
        if intro_msg_obj:
             try:
                 await intro_msg_obj.delete()
             except (discord.NotFound, discord.Forbidden, discord.HTTPException): pass # Ignore errors on cleanup
    else:
        await ctx.send("You are not currently playing Tic Tac Toe.")


@bot.command(name='scores', aliases=['tttscore'], help="Shows your TTT score vs the bot.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def show_scores(ctx):
    user_id = ctx.author.id
    user_score = user_tictactoe_scores.get(user_id, 0)
    # Access the global bot score
    global bot_tictactoe_score
    await ctx.send(f"📊 **Tic Tac Toe Scores**\n- {ctx.author.display_name}: {user_score}\n- {bot.user.name}: {bot_tictactoe_score}")


# --- Admin Commands ---
@bot.command(name='createchannel', hidden=True) # Hide from default help command
@commands.has_permissions(manage_channels=True) # User needs permission
@commands.bot_has_permissions(manage_channels=True) # Bot needs permission
@commands.cooldown(1, 60, commands.BucketType.guild) # Limit channel creation rate per guild
async def createchannel(ctx, channel_name: str):
    """(Admin) Creates a new text channel. Requires Manage Channels permission."""
    guild = ctx.guild
    # Basic sanitization: lowercase, replace spaces with dashes, allow letters/numbers/dash/underscore
    safe_channel_name = ''.join(c for c in channel_name.lower().replace(' ', '-') if c.isalnum() or c in ('-', '_'))[:100] # Limit length

    # Prevent creating empty or invalid names after sanitization
    if not safe_channel_name or safe_channel_name in ['-', '_'] * len(safe_channel_name): # Check if only separators remain
        await ctx.send("❌ Invalid channel name provided. Please use alphanumeric characters, spaces, dashes, or underscores.")
        return

    # Check if channel already exists (case-insensitive check via discord.utils)
    existing_channel = discord.utils.get(guild.text_channels, name=safe_channel_name)
    if not existing_channel:
        try:
            # Specify category if desired, otherwise creates at top level or default category
            # category = discord.utils.get(guild.categories, name="Bots") # Example category
            # new_channel = await guild.create_text_channel(safe_channel_name, category=category)
            new_channel = await guild.create_text_channel(safe_channel_name)
            await ctx.send(f'✅ Text channel {new_channel.mention} created successfully!')
        # Specific exceptions already handled by on_command_error, but can catch here too for context
        except discord.Forbidden:
            await ctx.send("❌ I lack the 'Manage Channels' permission to do that.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to create channel due to a Discord API error (Status: {e.status}, Code: {e.code}).")
        except Exception as e:
             # Catch any other unexpected errors during channel creation
             await ctx.send(f"❌ An unexpected error occurred during channel creation: {e}")
             print(f"!!! Error in createchannel command: {e}")
             traceback.print_exc()
    else:
        await ctx.send(f'❌ A text channel named `{safe_channel_name}` already exists!')

# --- Run the bot ---
if __name__ == "__main__":
    bot_token = os.getenv('DISCORD_TOKEN')
    if not bot_token:
        print("--- FATAL ERROR ---")
        print("Error: DISCORD_TOKEN not found in environment variables or .env file.")
        print("1. Ensure you have a file named '.env' in the same directory as this script.")
        print("2. Ensure the .env file contains a line like: DISCORD_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE")
        print("-------------------")
        sys.exit(1) # Exit if no token is found

    try:
        print("Attempting to connect to Discord...")
        # Running the bot initializes the connection and event loop
        bot.run(bot_token)
    except discord.LoginFailure:
        print("--- FATAL ERROR ---")
        print("Error: Login Failed - Invalid Discord Token.")
        print("Please verify the DISCORD_TOKEN in your .env file or environment variables.")
        print("It might be incorrect, expired, or revoked.")
        print("-------------------")
    except discord.PrivilegedIntentsRequired:
        print("--- FATAL ERROR ---")
        print("Error: Privileged Intents Required but not enabled.")
        print("You MUST enable the following intents in your bot's application page on discord.com/developers/applications:")
        print("  - PRESENCE INTENT (if using presence features - currently not essential for this code)")
        print("  - SERVER MEMBERS INTENT (if using member features - currently not essential for this code)")
        print("  - MESSAGE CONTENT INTENT (REQUIRED for reading commands and game inputs)")
        print("Make sure the toggles are ON in the 'Privileged Gateway Intents' section.")
        print("-------------------")
    except Exception as e:
        # Catch any other unexpected errors during the bot's runtime startup
        print(f"--- FATAL ERROR ---")
        print(f"An unexpected error occurred while starting or running the bot: {e}")
        print("-------------------")
        traceback.print_exc() # Print the full traceback for debugging
    finally:
         print("Bot process has exited.")