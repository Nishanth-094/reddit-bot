# Blueberry Bot
This bot brings the characters from Friends to life in your Discord server. Play games, earn points, unlock new character interactions, and experience classic friends moments — complete with pizza, sarcasm, and surprises.

## Track and Contributors
***Track***: Discord-Arcade

**Contributors***:
Brinda (Brixbriu)
Yashaswini(yashaswini450)
Nishanth(Nishanth-094)

## Problem Statement
Making an arcade themed bot for HackNite2k25 organized by Zense club of IIITB.
## Goal
To create a Discord bot(Blueberry Bot) your server.
## Features
1ST LEVEL:
- joey fun trivia
- 6-round Rock-Paper-Scissors game using Discord buttons
- Chandler keeps score and delivers classic snarky commentary
- Points system:  
  - ✅ Win = +7 points  
  - ❌ Loss = -3 points  
  - 🤝 Tie = 0 points
- Timeout mechanic: users have 15 seconds per round
- Phoebe surprises users at the end with some wild energy and the next `!pheebs` command tease
- ross - wordle game

COMMANDS :
!rps – starts the 6-round rock-paper-scissors game with chandler commentary
!pheebs- teased at the end for future interactions with phoebe.
More below!!

🧔 Joey Tribbiani
- **Voice interaction**: Joey greets you with a *"How you doin'?"* line when you're in a voice channel.
- **Gift system**: Give Joey something he loves and earn points. Give him the wrong item... and face his judgment.
- **Trivia game**: Join Joey in a pizza-fueled story with a multiple choice question. Get it right and Chandler shows up.
- **Classic Joey quotes**: Trigger famous Joey lines with `!joeyline`.

 😎 Chandler Bing
- **Rock-Paper-Scissors game**: Play 6 rounds of RPS with Chandler. Win or lose points based on how you play.
- **Sarcastic feedback**: Chandler roasts you based on your score.
- **Unlockable character**: Earn Chandler by getting a trivia question right with Joey.
and many more.....

🎮 Commands
Command	Description
!talk	Joey joins your voice channel and says "How you doin'?"
!tell_story	Joey tells a story and asks a trivia question. Answer correctly to earn points and unlock Chandler.
!joeyline	Sends a classic Joey quote.
!gift <item>	Gift Joey something. If he likes it, you get points. If not, you lose some.
!rps	Play Rock-Paper-Scissors with Chandler over 6 rounds.
!pheebs	Phoebe makes a dramatic entrance with weirdness.
🔊 Audio Playback Setup
•	Make sure you have FFmpeg installed and added to your system's PATH.
•	Store Joey’s audio file at:
•	audio/Joey - Hey, How You Doin_.mp3

🥪 Gift Logic
Loved by Joey (+5 points)
•	pizza
•	meatball sub
•	sandwich
•	jacket
•	food
•	cologne
Disliked (-3 points)
Anything else — Joey is confused, disappointed, or just plain hungry.

### 🧙♀️ `!pheebs`
- Sends an image of **Smelly Cat** and asks users to guess the song.
- Responds based on the guess with Phoebe’s signature weirdness and wisdom.
- Rewards:
  - **Correct guess (smelly cat)**: +10 points
  - **Partial guess (cat)**: +3 points
  - **Wrong guess or timeout**: no points
- Bonus:
  - Plays *Smelly Cat* audio if the user is in a voice channel.
  - Follow-up dialogue includes a surprise visit from **Ross**, who introduces a Wordle-style game (`!wordle` coming soon).

### 🎸 `!phoebe`
- Sends a random iconic **Phoebe Buffay** quote to the channel.
🧠 Commands Summary
Command	Description
!pheebs	Guess the song based on a mysterious image
!phoebe	Sends a random quirky Phoebe quote

### 🟩 `!wordle`
- Starts a new Wordle game for the user.
- Selects a random 5-letter word from a preset list.
- The user has **6 attempts** to guess the correct word.
- Visual feedback is given using emoji blocks:
  - 🟩 Correct letter in the correct position
  - 🟨 Correct letter, wrong position
  - ⬜ Incorrect letter

### ⌨️ `!guess <word>`
- Submit a 5-letter word as a guess.
- Feedback is returned as a visual grid.
- At the end of the game:
  - If you win, **Rachel** shows up with a congrats message and image.
  - If you lose, **Rachel** still shows up—but with a burn.
Command	Description
!wordle	Start a new Wordle game
!guess <guess>	Submit a guess for the current Wordle game (ex !guess cards)

## Applications of Idea

- Enhancing community engagement and interaction within Discord servers.
- Providing entertainment and fun activities for users.