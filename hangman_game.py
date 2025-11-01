import tkinter as tk
from tkinter import messagebox
import requests
import random

# --- Constants ---
BG_COLOR = "#f2f2f2"
TITLE_COLOR = "#333333"
WORD_COLOR = "#000000"
INFO_COLOR = "#555555"
DRAW_COLOR = "#222222"
DRAW_WIDTH = 5

TITLE_FONT = ("Verdana", 28, "bold")
WORD_FONT = ("Courier", 34, "bold")
INFO_FONT = ("Arial", 14, "italic")
HINT_FONT = ("Arial", 12, "bold")
BUTTON_FONT = ("Arial", 12)
DIFFICULTY_BUTTON_FONT = ("Verdana", 14, "bold")

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

# API fetches 20 words, we filter them
API_BATCH_URL = "https://random-word-api.herokuapp.com/word?number=20" 

# Fallback words organized by difficulty
FALLBACK_WORDS = {
    "easy": ["TREE", "DOG", "SUN", "BOOK", "FISH"],
    "medium": ["PYTHON", "PROJECT", "GUITAR", "PLANET", "COOKIE"],
    "hard": ["PROGRAMMING", "UNIVERSITY", "ADVENTURE", "KNOWLEDGE"]
}

# Difficulty settings: (min_len, max_len, hints)
DIFFICULTY_SETTINGS = {
    "easy": (4, 6, 3),
    "medium": (7, 9, 2),
    "hard": (10, 30, 1) # 30 is just a high max
}

class HangmanGame:
    """
    A GUI-based Hangman game with difficulty levels and a hint system.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.secret_word = ""
        self.guesses = []
        self.errors = 0
        self.hints_left = 0
        self.difficulty = "medium" # Default

        # Create two main frames: one for the start screen, one for the game
        self.start_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.game_frame = tk.Frame(self.root, bg=BG_COLOR)
        
        # Pack the start frame initially
        self.start_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_start_screen()
        self.setup_game_screen() # Setup the game screen, but don't show it yet

        # Bind key presses to the handler function
        self.root.bind("<Key>", self.handle_key_press)

    def setup_start_screen(self):
        """Creates the UI elements for the start screen."""
        self.start_frame.columnconfigure(0, weight=1) # Center horizontally
        
        title_label = tk.Label(self.start_frame, 
                               text="Hangman", 
                               font=TITLE_FONT, 
                               bg=BG_COLOR, 
                               fg=TITLE_COLOR)
        title_label.pack(pady=(80, 20))

        info_label = tk.Label(self.start_frame, 
                              text="Choose your difficulty:", 
                              font=("Arial", 16), 
                              bg=BG_COLOR, 
                              fg=INFO_COLOR)
        info_label.pack(pady=20)
        
        button_frame = tk.Frame(self.start_frame, bg=BG_COLOR)
        button_frame.pack(pady=20)

        easy_button = tk.Button(button_frame, 
                                text="Easy", 
                                font=DIFFICULTY_BUTTON_FONT, 
                                command=lambda: self.start_game("easy"),
                                width=10)
        easy_button.pack(pady=10)

        medium_button = tk.Button(button_frame, 
                                  text="Medium", 
                                  font=DIFFICULTY_BUTTON_FONT, 
                                  command=lambda: self.start_game("medium"),
                                  width=10)
        medium_button.pack(pady=10)

        hard_button = tk.Button(button_frame, 
                                text="Hard", 
                                font=DIFFICULTY_BUTTON_FONT, 
                                command=lambda: self.start_game("hard"),
                                width=10)
        hard_button.pack(pady=10)

    def setup_game_screen(self):
        """Creates and places all the UI elements for the game itself."""
        
        # 1. Title (smaller, for in-game)
        self.game_title_label = tk.Label(self.game_frame, 
                                         text="Hangman", 
                                         font=TITLE_FONT, 
                                         bg=BG_COLOR, 
                                         fg=TITLE_COLOR)
        self.game_title_label.pack(pady=(20, 10))

        # 2. Canvas for drawing
        self.canvas = tk.Canvas(self.game_frame, 
                                width=400, 
                                height=250, 
                                bg=BG_COLOR, 
                                highlightthickness=0)
        self.canvas.pack(pady=10)

        # 3. Word label
        self.word_label = tk.Label(self.game_frame, 
                                   text="", 
                                   font=WORD_FONT, 
                                   bg=BG_COLOR, 
                                   fg=WORD_COLOR)
        self.word_label.pack(pady=(20, 10))

        # 4. Info label
        self.info_label = tk.Label(self.game_frame, 
                                   text="Type a letter to guess", 
                                   font=INFO_FONT, 
                                   bg=BG_COLOR, 
                                   fg=INFO_COLOR)
        self.info_label.pack(pady=5)
        
        # 5. Hint Label
        self.hint_label = tk.Label(self.game_frame,
                                   text="",
                                   font=HINT_FONT,
                                   bg=BG_COLOR,
                                   fg=INFO_COLOR)
        self.hint_label.pack(pady=5)

        # 6. Button Frame
        button_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        button_frame.pack(pady=20)

        self.new_game_button = tk.Button(button_frame, 
                                         text="Change Difficulty", # Renamed
                                         font=BUTTON_FONT,
                                         command=self.show_start_screen) # Changed command
        self.new_game_button.pack(side=tk.LEFT, padx=10)
        
        self.hint_button = tk.Button(button_frame,
                                       text="Get Hint",
                                       font=BUTTON_FONT,
                                       command=self.use_hint)
        self.hint_button.pack(side=tk.LEFT, padx=10)

    def start_game(self, difficulty):
        """Hides the start screen, shows the game screen, and starts a new game."""
        self.difficulty = difficulty
        
        # Switch frames
        self.start_frame.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        self.new_game()

    def show_start_screen(self):
        """Hides the game screen and shows the start screen."""
        self.game_frame.pack_forget()
        self.start_frame.pack(fill=tk.BOTH, expand=True)

    def load_words_from_api(self, difficulty):
        """Fetches a list of words and filters for one that matches the difficulty."""
        try:
            self.info_label.config(text="Fetching a new word...")
            self.root.update_idletasks()
            
            response = requests.get(API_BATCH_URL, timeout=5)
            response.raise_for_status()
            word_list = response.json()
            
            min_len, max_len, _ = DIFFICULTY_SETTINGS[difficulty]
            
            # Find a word that matches the criteria
            valid_words = [w for w in word_list if min_len <= len(w) <= max_len]
            
            if valid_words:
                self.info_label.config(text="Type a letter to guess")
                return random.choice(valid_words).upper()
            else:
                # If no words match, just pick one from the batch
                print("No word in batch matched criteria, picking random.")
                return random.choice(word_list).upper()

        except Exception as e:
            print(f"API Error: {e}")
            self.info_label.config(text="Type a letter to guess")
            return self.get_fallback_word(difficulty)

    def get_fallback_word(self, difficulty):
        """Returns a word from the fallback list based on difficulty."""
        print("Using fallback word list.")
        return random.choice(FALLBACK_WORDS[difficulty])

    def new_game(self):
        """Starts a new game by resetting all variables and UI elements."""
        
        self.errors = 0
        self.guesses = []
        
        # Get hints based on difficulty
        _, _, self.hints_left = DIFFICULTY_SETTINGS[self.difficulty]

        self.secret_word = self.load_words_from_api(self.difficulty)

        if not self.secret_word:
             messagebox.showerror("Error", "Could not get a new word. Check internet.")
             return

        self.canvas.delete("all")
        self.draw_gallows()
        self.update_word_label()
        self.info_label.config(text="Type a letter to guess")
        self.hint_label.config(text=f"Hints remaining: {self.hints_left}")
        
        self.hint_button.config(state=tk.NORMAL)

    def update_word_label(self):
        display_word = "".join(f"{letter} " if letter in self.guesses else "_ " for letter in self.secret_word)
        self.word_label.config(text=display_word.strip())

    def handle_key_press(self, event):
        if self.is_game_over() or self.start_frame.winfo_viewable():
            return # Don't process keys if game is over or on start screen

        guess = event.char.upper()
        if len(guess) == 1 and 'A' <= guess <= 'Z':
            self.process_guess(guess)

    def process_guess(self, guess):
        if guess in self.guesses:
            if not "Hint:" in self.info_label.cget("text"):
                self.info_label.config(text=f"You already guessed '{guess}'")
            return
        
        self.guesses.append(guess)
        
        if guess in self.secret_word:
            if not "Hint:" in self.info_label.cget("text"):
                self.info_label.config(text="Good guess!")
            self.update_word_label()
        else:
            self.errors += 1
            self.info_label.config(text=f"Wrong! '{guess}' is not in the word.")
            self.draw_hangman_part()
        
        self.check_game_over()

    def use_hint(self):
        if self.hints_left <= 0:
            self.info_label.config(text="No hints remaining!")
            return
        if self.is_game_over():
            return

        unguessed_letters = [letter for letter in self.secret_word if letter not in self.guesses]
        
        if not unguessed_letters:
            self.info_label.config(text="No more letters to guess!")
            return

        hint_letter = random.choice(unguessed_letters)
        self.hints_left -= 1
        self.hint_label.config(text=f"Hints remaining: {self.hints_left}")
        self.info_label.config(text=f"Hint: Revealing '{hint_letter}'!")
        
        self.process_guess(hint_letter)
        
        if self.hints_left <= 0:
            self.hint_button.config(state=tk.DISABLED)

    def draw_gallows(self):
        self.canvas.create_line(100, 220, 300, 220, width=DRAW_WIDTH, fill=DRAW_COLOR)
        self.canvas.create_line(150, 220, 150, 50, width=DRAW_WIDTH, fill=DRAW_COLOR)
        self.canvas.create_line(150, 50, 250, 50, width=DRAW_WIDTH, fill=DRAW_COLOR)
        self.canvas.create_line(250, 50, 250, 80, width=DRAW_WIDTH, fill=DRAW_COLOR)

    def draw_hangman_part(self):
        draw_funcs = [
            self.draw_head, self.draw_body, self.draw_left_arm,
            self.draw_right_arm, self.draw_left_leg, self.draw_right_leg
        ]
        if 0 < self.errors <= len(draw_funcs):
            draw_funcs[self.errors - 1]()

    def draw_head(self):
        self.canvas.create_oval(230, 80, 270, 120, width=DRAW_WIDTH, outline=DRAW_COLOR)
    def draw_body(self):
        self.canvas.create_line(250, 120, 250, 170, width=DRAW_WIDTH, fill=DRAW_COLOR)
    def draw_left_arm(self):
        self.canvas.create_line(250, 130, 220, 160, width=DRAW_WIDTH, fill=DRAW_COLOR)
    def draw_right_arm(self):
        self.canvas.create_line(250, 130, 280, 160, width=DRAW_WIDTH, fill=DRAW_COLOR)
    def draw_left_leg(self):
        self.canvas.create_line(250, 170, 220, 200, width=DRAW_WIDTH, fill=DRAW_COLOR)
    def draw_right_leg(self):
        self.canvas.create_line(250, 170, 280, 200, width=DRAW_WIDTH, fill=DRAW_COLOR)

    def is_game_over(self):
        if self.errors >= 6:
            return True
        if all(letter in self.guesses for letter in self.secret_word):
            return True
        return False

    def check_game_over(self):
        game_won = all(letter in self.guesses for letter in self.secret_word)
        game_lost = self.errors >= 6

        if not game_won and not game_lost:
            return

        self.hint_button.config(state=tk.DISABLED)

        if game_won:
            self.info_label.config(text="You won! Congratulations!")
            messagebox.showinfo("Hangman", f"You won!\nThe word was: {self.secret_word}")
        
        elif game_lost:
            self.info_label.config(text="Game Over!")
            messagebox.showinfo("Hangman", f"Game Over!\nThe word was: {self.secret_word}")
            
        # The "ask_play_again" is now handled by the "Change Difficulty" button
        # We just leave the user on the game over screen

if __name__ == "__main__":
    main_window = tk.Tk()
    game = HangmanGame(main_window)
    main_window.mainloop()

