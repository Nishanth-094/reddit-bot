import random

GREEN = "🟩"
YELLOW = "🟨"
GRAY = "⬜"

WORDS = ["apple", "grape", "brick", "crane", "stone", "flame", "pride", "sweet"]

def get_random_word():
    return random.choice(WORDS)

def get_feedback(secret, guess):
    result = [""] * 5
    secret_letters = list(secret)

    for i in range(5):
        if guess[i] == secret[i]:
            result[i] = GREEN
            secret_letters[i] = None
        else:
            result[i] = None

    for i in range(5):
        if result[i] is None:
            if guess[i] in secret_letters:
                result[i] = YELLOW
                secret_letters[secret_letters.index(guess[i])] = None
            else:
                result[i] = GRAY

    return "".join(result)
