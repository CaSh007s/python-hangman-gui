# Python Hangman GUI

A modern, graphical Hangman game built with Python and Tkinter. This is not your typical command-line game; it features a clean user interface, dynamic words fetched from a live API, and selectable difficulty levels.

![Hangman Game UI](https://placehold.co/600x400/f2f2f2/333333?text=Add+a+Screenshot+of+your+Game+Here)
*(Suggestion: Use a tool like Giphy Capture or ShareX to create a short GIF of your game in action and replace the placeholder image above!)*

---

## Features

* **Clean GUI:** A simple and intuitive two-screen interface built with Python's built-in Tkinter library.
* **Dynamic Word Generation:** Forget static word lists! This game fetches random words in real-time from the [Random Word API](https://random-word-api.herokuapp.com/), so you get a new challenge every time.
* **Difficulty Levels:** Choose your challenge!
    * **Easy:** Short words (4-6 letters) & 3 hints.
    * **Medium:** Mid-length words (7-9 letters) & 2 hints.
    * **Hard:** Long words (10+ letters) & only 1 hint.
* **Hint System:** Stuck on a word? Use one of your limited hints to get a random, correct letter.
* **Responsive Feedback:** The game provides real-time feedback on your guesses, tracks your remaining hints, and draws the hangman for each incorrect guess.
* **Fallback Included:** If the API is unreachable, the game gracefully falls back to a built-in word list to ensure it's always playable.

---

## How to Run This Project

### Prerequisites

* Python 3.x
* `pip` (Python's package installer)
* `git` (for cloning)

### Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
    cd YOUR_REPOSITORY
    ```

2.  **Create and activate a virtual environment:**
    *This is the recommended way to keep dependencies clean.*

    * On Windows:
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install the required packages:**
    *The only external dependency is `requests` (for the API).*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the game!**
    ```bash
    python hangman_game.py
    ```

---

## File Structure
```bash
python_hangman_gui/ │ ├── .gitignore # Tells Git to ignore the virtual environment ├── hangman_game.py # The complete, single-file Python application ├── requirements.txt # Lists the single 'requests' dependency └── README.md```
