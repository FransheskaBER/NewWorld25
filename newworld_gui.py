import tkinter as tk
import sys
import threading
import queue

# Queue to pass input() text from Entry to game thread
input_queue = queue.Queue()

# --- Redirect stdout (print) ---
class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # auto-scroll

    def flush(self):
        pass

# --- Replace input() ---
def gui_input(prompt=""):
    # Show prompt in the text area
    sys.stdout.write(prompt)

    # Wait until user submits something in Entry
    return input_queue.get()   # blocks until .put() is called

def submit_input():
    user_text = entry.get()
    entry.delete(0, tk.END)
    # Echo the input into the Text area, just like a real terminal
    text.insert(tk.END, user_text + "\n")
    text.see(tk.END)
    input_queue.put(user_text)  # send input to game thread

# --- Run your game in thread ---
def run_game():
    import builtins
    from main import Game

    # Replace built-in input with our gui_input
    builtins.input = gui_input

    # Now run the game exactly as-is
    game = Game()
    game.setup()
    while not game.play_round():   # example game loop
        pass

def start_game():
    thread = threading.Thread(target=run_game, daemon=True)
    thread.start()

# --- Tkinter GUI ---
root = tk.Tk()
root.title("NewWorld 2025")

# Big text area (acts like terminal)
text = tk.Text(root, bg="white", fg="black", font=("Courier", 12))
text.pack(expand=True, fill="both")

# Redirect stdout/stderr
redir = RedirectText(text)
sys.stdout = redir
sys.stderr = redir

# Input entry + submit button
frame = tk.Frame(root)
frame.pack(fill="x")
entry = tk.Entry(frame, width=20, bg="lightyellow", fg="black") # calculate the width, background of the textbox
entry.pack(side="left", padx=5, pady=5) # padx or pady is padding

submit_btn = tk.Button(frame, text="Submit", command=submit_input, bg="lightyellow", fg="black")
submit_btn.pack(side="left", padx=5, pady=5)

# Start button
tk.Button(root, text="Start Game", command=start_game, bg="lightyellow", fg="black").pack(pady=50)

root.mainloop()
