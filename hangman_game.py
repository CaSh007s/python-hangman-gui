import tkinter as tk
from tkinter import messagebox
import requests
import random
import threading

# --- Constants ---
BG_COLOR = "#f2f2f2"
TITLE_COLOR = "#333333"
WORD_COLOR = "#000000"
INFO_COLOR = "#555555"
DRAW_COLOR = "#222222"
DRAW_WIDTH = 5
BUTTON_BG = "#e0e0e0"
BUTTON_FG = "#111111"
BUTTON_ACTIVE_BG = "#cccccc"

TITLE_FONT = ("Verdana", 28, "bold")
WORD_FONT = ("Courier", 32, "bold")
INFO_FONT = ("Arial", 14, "italic")
BUTTON_FONT = ("Arial", 12, "bold")
HINT_FONT = ("Arial", 12)
DIFFICULTY_FONT = ("Arial", 16, "bold")

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 650

API_BATCH_URL = "https://random-word-api.herokuapp.com/word?number=20"
FALLBACK_WORDS = ["PYTHON", "PROJECT", "GITHUB", "HANGMAN", "TKINTER", "DEVELOPER"]

# Difficulty settings: (min_len, max_len, hints)
DIFFICULTY_SETTINGS = {
    "easy": (4, 6, 3),
    "medium": (7, 9, 2),
    "hard": (10, 30, 1)
}

# --- HangmanGame Class ---

class HangmanGame:
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
        self.game_over = False

        self.setup_ui()
        self.show_start_screen()
        
        # Bind key press event
        self.root.bind("<Key>", self.handle_key_press)

    def setup_ui(self):
        """Sets up the two main frames: start and game."""
        
        # --- Start Screen Frame ---
        self.start_frame = tk.Frame(self.root, bg=BG_COLOR)
        
        tk.Label(self.start_frame, text="Hangman", font=TITLE_FONT, bg=BG_COLOR, fg=TITLE_COLOR).pack(pady=(50, 30))
        tk.Label(self.start_frame, text="Choose your difficulty:", font=DIFFICULTY_FONT, bg=BG_COLOR, fg=INFO_COLOR).pack(pady=(0, 20))

        easy_btn = tk.Button(self.start_frame, text="Easy", font=DIFFICULTY_FONT, command=lambda: self.start_game("easy"), bg="#90ee90", fg=BUTTON_FG, width=15)
        easy_btn.pack(pady=10)
        
        medium_btn = tk.Button(self.start_frame, text="Medium", font=DIFFICULTY_FONT, command=lambda: self.start_game("medium"), bg="#f0e68c", fg=BUTTON_FG, width=15)
        medium_btn.pack(pady=10)
        
        hard_btn = tk.Button(self.start_frame, text="Hard", font=DIFFICULTY_FONT, command=lambda: self.start_game("hard"), bg="#ff6347", fg=BUTTON_FG, width=15)
        hard_btn.pack(pady=10)

        # --- Game Screen Frame ---
        self.game_frame = tk.Frame(self.root, bg=BG_COLOR)
        
        self.title_label = tk.Label(self.game_frame, text="Hangman", font=TITLE_FONT, bg=BG_COLOR, fg=TITLE_COLOR)
        self.title_label.pack(pady=(10, 5))

        self.canvas = tk.Canvas(self.game_frame, width=400, height=300, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.word_label = tk.Label(self.game_frame, text="", font=WORD_FONT, bg=BG_COLOR, fg=WORD_COLOR)
        self.word_label.pack(pady=10)

        self.info_label = tk.Label(self.game_frame, text="Type a letter to guess", font=INFO_FONT, bg=BG_COLOR, fg=INFO_COLOR)
        self.info_label.pack(pady=5)
        
        self.hint_label = tk.Label(self.game_frame, text="", font=HINT_FONT, bg=BG_COLOR, fg=INFO_COLOR)
        self.hint_label.pack(pady=5)

        # Button frame for game controls
        self.button_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        self.button_frame.pack(pady=20)

        self.replay_button = tk.Button(self.button_frame, text="Replay", font=BUTTON_FONT, bg=BUTTON_BG, fg=BUTTON_FG,
                                       activebackground=BUTTON_ACTIVE_BG, command=self.new_game)
        self.replay_button.grid(row=0, column=0, padx=10)

        self.hint_button = tk.Button(self.button_frame, text="Hint", font=BUTTON_FONT, bg=BUTTON_BG, fg=BUTTON_FG,
                                     activebackground=BUTTON_ACTIVE_BG, command=self.use_hint)
        self.hint_button.grid(row=0, column=1, padx=10)
        
        self.difficulty_button = tk.Button(self.button_frame, text="Change Difficulty", font=BUTTON_FONT, bg=BUTTON_BG, fg=BUTTON_FG,
                                           activebackground=BUTTON_ACTIVE_BG, command=self.show_start_screen)
        self.difficulty_button.grid(row=0, column=2, padx=10)


    def show_start_screen(self):
        """Hides the game screen and shows the start screen."""
        self.game_frame.pack_forget()
        self.start_frame.pack(fill="both", expand=True)
        self.game_over = True # Prevent key presses on start screen

    def start_game(self, difficulty):
        """Hides the start screen, shows the game screen, and starts a new game."""
        self.difficulty = difficulty
        self.start_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.new_game()

    def load_words_from_api(self):
        """Fetches a batch of words and filters for difficulty."""
        try:
            response = requests.get(API_BATCH_URL, timeout=5)
            if response.status_code == 200:
                words = response.json()
                min_len, max_len, _ = DIFFICULTY_SETTINGS[self.difficulty]
                
                valid_words = [w.upper() for w in words if min_len <= len(w) <= max_len]
                
                if valid_words:
                    return random.choice(valid_words)
            
            # Fallback if API fails or no words match criteria
            return self.get_fallback_word()
            
        except requests.RequestException as e:
            print(f"API Error: {e}. Using fallback word.")
            return self.get_fallback_word()

    def get_fallback_word(self):
        """Gets a fallback word based on difficulty."""
        min_len, max_len, _ = DIFFICULTY_SETTINGS[self.difficulty]
        valid_words = [w for w in FALLBACK_WORDS if min_len <= len(w) <= max_len]
        
        if valid_words:
            return random.choice(valid_words)
        else:
            # If no fallback matches, just pick any fallback
            return random.choice(FALLBACK_WORDS)

    def new_game(self):
        """Starts a new game by resetting all variables and UI elements."""
        
        # Disable buttons and show loading text
        self.set_game_controls_state("disabled")
        self.info_label.config(text="Fetching a new word...")
        self.word_label.config(text="")
        
        # Run API call in a separate thread to keep UI responsive
        threading.Thread(target=self.new_game_thread, daemon=True).start()

    def new_game_thread(self):
        """The part of new_game that runs in a thread (network call)."""
        
        self.secret_word = self.load_words_from_api()
        
        # Once word is fetched, update UI from the main thread
        self.root.after(0, self.new_game_ui_update)

    def new_game_ui_update(self):
        """Updates the UI after the new word has been fetched."""
        if not self.secret_word:
             messagebox.showerror("Error", "Could not get a new word. Please check internet.")
             self.show_start_screen()
             return
             
        self.errors = 0
        self.guesses = []
        self.game_over = False
        _, _, self.hints_left = DIFFICULTY_SETTINGS[self.difficulty]

        self.canvas.delete("all")
        self.draw_gallows()
        self.update_word_label()
        self.info_label.config(text="Type a letter to guess")
        self.hint_label.config(text=f"Hints remaining: {self.hints_left}")
        
        # Re-enable buttons
        self.set_game_controls_state("normal")
        if self.hints_left == 0:
            self.hint_button.config(state="disabled")

    def set_game_controls_state(self, state):
        """Disables or enables all game control buttons."""
        self.replay_button.config(state=state)
        self.hint_button.config(state=state)
        self.difficulty_button.config(state=state)

    def update_word_label(self):
        """Updates the word label (e.g., P _ T H _ N)"""
        display_word = ""
        for letter in self.secret_word:
            if letter in self.guesses:
                display_word += letter + " "
            else:
                display_word += "_ "
        self.word_label.config(text=display_word.strip())

    def handle_key_press(self, event):
        """Handles a key press event from the user."""
        if self.game_over:
            return # Don't process keys if game is over or on start screen

        try:
            char = event.char.upper()
            if 'A' <= char <= 'Z':
                self.process_guess(char)
        except AttributeError:
            # This can happen on special keys like 'Shift'
            pass

    def process_guess(self, letter):
        """Processes a valid letter guess."""
        if letter in self.guesses:
            self.info_label.config(text=f"You already guessed '{letter}'")
            return

        self.guesses.append(letter)

        if letter in self.secret_word:
            self.info_label.config(text="Correct guess!")
            self.update_word_label()
        else:
            self.info_label.config(text=f"Wrong guess: '{letter}'")
            self.errors += 1
            self.draw_hangman_part()

        self.check_game_over()

    def use_hint(self):
        """Uses a hint to reveal a correct, unguessed letter."""
        if self.hints_left <= 0 or self.game_over:
            return

        # Find all correct letters that haven't been guessed yet
        unguessed_letters = [
            letter for letter in self.secret_word if letter not in self.guesses
        ]

        if unguessed_letters:
            self.hints_left -= 1
            self.hint_label.config(text=f"Hints remaining: {self.hints_left}")
            
            # Get a random hint
            hint_letter = random.choice(unguessed_letters)
            
            # Process it as a guess
            self.info_label.config(text=f"Hint used! Revealed: '{hint_letter}'")
            self.process_guess(hint_letter)
        
        if self.hints_left == 0:
            self.hint_button.config(state="disabled")

    def draw_gallows(self):
        """Draws the initial hangman gallows."""
        self.canvas.create_line(100, 280, 300, 280, width=DRAW_WIDTH, fill=DRAW_COLOR) # Base
        self.canvas.create_line(150, 280, 150, 50, width=DRAW_WIDTH, fill=DRAW_COLOR)  # Pole
        self.canvas.create_line(150, 50, 250, 50, width=DRAW_WIDTH, fill=DRAW_COLOR)  # Beam
        self.canvas.create_line(250, 50, 250, 80, width=DRAW_WIDTH, fill=DRAW_COLOR)  # Rope

    def draw_hangman_part(self):
        """Draws the next part of the hangman based on the error count."""
        if self.errors == 1: # Head
            self.canvas.create_oval(230, 80, 270, 120, width=DRAW_WIDTH, outline=DRAW_COLOR)
        elif self.errors == 2: # Torso
            self.canvas.create_line(250, 120, 250, 190, width=DRAW_WIDTH, fill=DRAW_COLOR)
        elif self.errors == 3: # Left Arm
            self.canvas.create_line(250, 140, 220, 170, width=DRAW_WIDTH, fill=DRAW_COLOR)
        elif self.errors == 4: # Right Arm
            self.canvas.create_line(250, 140, 280, 170, width=DRAW_WIDTH, fill=DRAW_COLOR)
        elif self.errors == 5: # Left Leg
            self.canvas.create_line(250, 190, 220, 230, width=DRAW_WIDTH, fill=DRAW_COLOR)
        elif self.errors == 6: # Right Leg
            self.canvas.create_line(250, 190, 280, 230, width=DRAW_WIDTH, fill=DRAW_COLOR)

    def check_game_over(self):
        """Checks if the game has been won or lost."""
        if self.game_over:
            return

        # Check for a win
        if all(letter in self.guesses for letter in self.secret_word):
            self.info_label.config(text="You Win! Congratulations!")
            self.game_over = True
            self.hint_button.config(state="disabled")

        # Check for a loss
        elif self.errors >= 6:
            self.info_label.config(text=f"You Lose! The word was: {self.secret_word}")
            self.game_over = True
            self.hint_button.config(state="disabled")
            # Reveal the word
            self.word_label.config(text=" ".join(list(self.secret_word)))


# --- Main execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    game = HangmanGame(main_window)
    main_window.mainloop()

