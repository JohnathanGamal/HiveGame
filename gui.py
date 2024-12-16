import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import math

from engine import HiveGame
from hiveAI import HiveAI


class HiveGameGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Hive Game")
        self.root.geometry("1280x720")
        self.root.configure(bg="#2e3b4e")

        # Game settings
        self.board_size = 20
        self.cell_size = 50
        self.game_mode = None  # Game mode (PvP, PvC, CvC)
        self.selected_piece_to_move = None
        self.selected_piece_coord = (None, None)
        self.selected_piece_valid_moves = None
        self.first_play = True
        self.max_depth = []
        self.time_limit = []
        self.current_character = tk.StringVar(value="Bee")  # Default character
        self.colors = {
            "Player 1": "#3498db",
            "Player 2": "#e74c3c",
            "None": "#000000",
            "selection": "#00ff00",
            "moves": "#663399"
        }
        # Load character images
        self.original_images = {
            "Bee": Image.open("bee.png"),
            "Ant": Image.open("ant.png"),
            "Spider": Image.open("spider.png"),
            "Grasshopper": Image.open("grasshopper.png"),
            "Beetle": Image.open("beetle.png"),
        }
        self.character_images = self.resize_images()

        # Backend trackers
        self.backend = HiveGame(board_size=self.board_size)
        self.board = self.backend.boardState.board
        self.ai = HiveAI(self.backend)

        self.current_player = self.backend.current_player
        self.turn_counter = self.backend.turn_counter
        self.bee_coordinates = self.backend.bee_coordinates
        self.bee_placed = self.backend.bee_placed
        # Track pieces left for each player
        self.player_pieces = self.backend.player_pieces
        self.pieces_on_board = self.backend.boardState.pieces_on_board

        # Show the game mode selection screen
        self.show_game_mode_selection()

    def show_game_mode_selection(self):
        """Show a menu for selecting the game mode before starting the game."""
        self.menu_frame = tk.Frame(self.root, bg="#34495e", width=1200, height=700)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = tk.Label(self.menu_frame, text="Choose Game Mode", font=("Segoe UI", 24, "bold"), bg="#34495e",
                                fg="white")
        header_label.pack(pady=50)

        # Buttons for game mode selection
        pvp_button = tk.Button(self.menu_frame, text="PvP: Player vs Player", font=("Segoe UI", 18), bg="#3498db",
                               fg="white", command=self.start_pvp_game)
        pvp_button.pack(pady=10, fill=tk.X)

        pvc_button = tk.Button(self.menu_frame, text="PvC: Player vs Computer", font=("Segoe UI", 18), bg="#3498db",
                               fg="white", command=lambda: self.show_difficulty_selection("PvC"))
        pvc_button.pack(pady=10, fill=tk.X)

        cvc_button = tk.Button(self.menu_frame, text="CvC: Computer vs Computer", font=("Segoe UI", 18), bg="#3498db",
                               fg="white", command=lambda: self.show_difficulty_selection("CvC"))
        cvc_button.pack(pady=10, fill=tk.X)

    def show_difficulty_selection(self, game_mode):
        """Show a menu for selecting the AI difficulty before starting a PvP or PvC game."""
        self.menu_frame.pack_forget()  # Hide the game mode selection menu
        self.menu_frame = tk.Frame(self.root, bg="#34495e", width=1200, height=700)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

        title = "Choose Game Difficulty" if game_mode == "PvC" else "Choose Difficulty For PC " + str(
            len(self.max_depth) + 1)

        # Header
        header_label = tk.Label(self.menu_frame, text=title, font=("Segoe UI", 24, "bold"), bg="#34495e",
                                fg="white")
        header_label.pack(pady=50)

        # Buttons for game mode selection
        easy_mode_button = tk.Button(self.menu_frame, text="EASY", font=("Segoe UI", 18), bg="#3498db",
                                     fg="white", command=lambda: self.set_ai_difficulty(game_mode, "easy"))
        easy_mode_button.pack(pady=10, fill=tk.X)

        medium_mode_button = tk.Button(self.menu_frame, text="MEDIUM", font=("Segoe UI", 18), bg="#3498db",
                                       fg="white", command=lambda: self.set_ai_difficulty(game_mode, "medium"))
        medium_mode_button.pack(pady=10, fill=tk.X)

        hard_mode_button = tk.Button(self.menu_frame, text="HARD", font=("Segoe UI", 18), bg="#3498db",
                                     fg="white", command=lambda: self.set_ai_difficulty(game_mode, "hard"))
        hard_mode_button.pack(pady=10, fill=tk.X)

    def set_ai_difficulty(self, game_mode, game_difficulty):
        max_depth = {
            "easy": 1,
            "medium": 2,
            "hard": 50
        }

        time_limit = {
            "easy": 2,
            "medium": 5,
            "hard": 12
        }

        self.max_depth.append(max_depth[game_difficulty])
        self.time_limit.append(time_limit[game_difficulty])

        if game_mode == "CvC" and len(self.max_depth) == 1:
            self.show_difficulty_selection(game_mode)
            return

        if game_mode == "PvC":
            self.start_pvc_game()

        if game_mode == "CvC":
            self.start_cvc_game()

    def start_pvp_game(self):
        """Start the PvP game."""
        self.game_mode = "PvP"
        self.menu_frame.pack_forget()  # Hide the game mode selection menu
        self.setup_game()

    def start_pvc_game(self):
        """Start the PvC game."""
        self.game_mode = "PvC"
        self.menu_frame.pack_forget()  # Hide the game mode selection menu
        self.setup_game()

    def start_cvc_game(self):
        """Start the CvC game."""
        self.game_mode = "CvC"
        self.menu_frame.pack_forget()  # Hide the game mode selection menu
        self.setup_game()
        self.root.after(1000, self.computer_move)

    def setup_game(self):
        """Setup the board and start the game logic."""
        self.frame = tk.Frame(self.root, bg="#ffffff")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(self.frame, bg="#ffffff", scrollregion=(0, 0,
                                                                        self.board_size * self.cell_size * 1.5,
                                                                        self.board_size * self.cell_size * math.sqrt(
                                                                            3)))
        self.h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Draw the grid
        self.draw_grid()

        # Center the canvas view
        self.root.update_idletasks()  # Ensure geometry is updated before calculations
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        scroll_region = self.canvas.cget("scrollregion").split()
        scroll_width = float(scroll_region[2])
        scroll_height = float(scroll_region[3])

        x_center = (scroll_width - canvas_width) / 2 / scroll_width
        y_center = (scroll_height - canvas_height) / 2 / scroll_height

        self.canvas.xview_moveto(x_center)
        self.canvas.yview_moveto(y_center)
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_click)

        # Info panel
        self.info_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        self.info_frame.pack(fill=tk.X, padx=20, pady=(10, 0))

        self.info_label = tk.Label(self.info_frame, text=f"{self.current_player}'s Turn", font=("Segoe UI", 16, "bold"),
                                   bg="#2c3e50", fg="white")
        self.info_label.pack(side=tk.LEFT, padx=10)

        # Character selection
        tk.Label(self.info_frame, text="Choose Character:", font=("Segoe UI", 12), bg="#2c3e50", fg="white").pack(
            side=tk.LEFT, padx=10)
        self.character_menu = ttk.Combobox(self.info_frame, textvariable=self.current_character,
                                           values=list(self.original_images.keys()), state="readonly",
                                           font=("Segoe UI", 12))
        self.character_menu.pack(side=tk.LEFT, padx=10)

        # Show remaining pieces for each player
        self.piece_count_label = tk.Label(self.info_frame, text=self.get_piece_count_text(), font=("Segoe UI", 12),
                                          bg="#2c3e50", fg="white")
        self.piece_count_label.pack(side=tk.LEFT, expand=True, anchor="center")

        # Show Reset Button
        reset_button = tk.Button(self.info_frame, text="Restart", font=("Segoe UI", 16), bg="#e74c3c",
                                 fg="white", command=self.reset_game)
        reset_button.pack(side=tk.RIGHT, padx=10)