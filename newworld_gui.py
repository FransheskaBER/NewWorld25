import tkinter as tk
from main import Game

# Global variable for the game object
game = None

# --- Functions ---
def start_game(num_players):
    global game
    game = Game()
    game.setup(num_players)   # IMPORTANT: make sure your setup() accepts num_players
    show_main_ui()

def show_main_ui():
    # Clear the start screen
    for widget in root.winfo_children():
        widget.destroy()

    # --- Top (Bank Info) ---
    top_frame = tk.Frame(root, pady=10)
    top_frame.pack(side="top", fill="x")
    global bank_label
    bank_label = tk.Label(top_frame, text="Bank Resources | Features | Milestones", font=("Arial", 14))
    bank_label.pack()

    # --- Middle (Players + Board) ---
    middle_frame = tk.Frame(root, padx=10, pady=10)
    middle_frame.pack(expand=True, fill="both")

    # Player 1 panel
    global p1_label, p2_label
    p1_frame = tk.Frame(middle_frame, width=200, bd=2, relief="groove")
    p1_frame.pack(side="left", fill="y")
    p1_label = tk.Label(p1_frame, text="Player 1 Stats", justify="left")
    p1_label.pack(padx=5, pady=5)

    # Board
    global board_text
    board_frame = tk.Frame(middle_frame, bd=2, relief="sunken")
    board_frame.pack(side="left", expand=True, fill="both", padx=10)
    board_text = tk.Label(board_frame, text="Game Board Output", font=("Arial", 16), wraplength=400, justify="center")
    board_text.pack(expand=True)

    # Player 2 panel (always create, hide if only 2 players)
    p2_frame = tk.Frame(middle_frame, width=200, bd=2, relief="groove")
    p2_frame.pack(side="right", fill="y")
    p2_label = tk.Label(p2_frame, text="Player 2 Stats", justify="left")
    p2_label.pack(padx=5, pady=5)

    # --- Bottom (Buttons) ---
    bottom_frame = tk.Frame(root, pady=10)
    bottom_frame.pack(side="bottom", fill="x")

    # Action buttons
    action_frame = tk.LabelFrame(bottom_frame, text="Actions")
    action_frame.pack(side="top", fill="x", pady=5)
    for action in ["Gather", "Build", "Claim", "Development"]:
        btn = tk.Button(action_frame, text=action, width=12,
                        command=lambda a=action: handle_action(a))
        btn.pack(side="left", padx=5)

    # Resource buttons
    resource_frame = tk.LabelFrame(bottom_frame, text="Resources")
    resource_frame.pack(side="top", fill="x", pady=5)
    for num in [1, 2, 3]:
        btn = tk.Button(resource_frame, text=str(num), width=5,
                        command=lambda n=num: handle_resource(n))
        btn.pack(side="left", padx=5)

    # Feature buttons
    feature_frame = tk.LabelFrame(bottom_frame, text="Features")
    feature_frame.pack(side="top", fill="x", pady=5)
    for letter in ["A", "B", "C"]:
        btn = tk.Button(feature_frame, text=letter, width=5,
                        command=lambda l=letter: handle_feature(l))
        btn.pack(side="left", padx=5)

    # Milestone buttons
    milestone_frame = tk.LabelFrame(bottom_frame, text="Milestones")
    milestone_frame.pack(side="top", fill="x", pady=5)
    for letter in ["X", "Y", "Z"]:
        btn = tk.Button(milestone_frame, text=letter, width=5,
                        command=lambda l=letter: handle_milestone(l))
        btn.pack(side="left", padx=5)

    # Show initial stats
    update_labels()


def handle_action(choice):
    # Example: integrate with game logic
    board_text.config(text=f"Action chosen: {choice}")
    # game.play_round(choice)   # integrate when ready
    update_labels()

def handle_resource(number):
    board_text.config(text=f"Resource chosen: {number}")
    update_labels()

def handle_feature(letter):
    board_text.config(text=f"Feature chosen: {letter}")
    update_labels()

def handle_milestone(letter):
    board_text.config(text=f"Milestone chosen: {letter}")
    update_labels()

def update_labels():
    try:
        p1 = game.players[0]
        p1_label.config(text=f"{p1.name}\nPoints: {getattr(p1, 'points', '?')}")
    except Exception as e:
        p1_label.config(text=f"Error P1: {e}")

    if len(game.players) > 1:
        try:
            p2 = game.players[1]
            p2_label.config(text=f"{p2.name}\nPoints: {getattr(p2, 'points', '?')}")
        except Exception as e:
            p2_label.config(text=f"Error P2: {e}")

    bank_label.config(text="Bank: (replace with real data later)")

# --- Root window ---
root = tk.Tk()
root.title("NewWorld 2025")
root.geometry("1000x700")

# --- Start Screen ---
tk.Label(root, text="Choose number of players:", font=("Arial", 16)).pack(pady=20)
tk.Button(root, text="2 Players", width=15, command=lambda: start_game(2)).pack(pady=10)
tk.Button(root, text="3 Players", width=15, command=lambda: start_game(3)).pack(pady=10)

root.mainloop()
