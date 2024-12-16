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

        def reset_game(self):
            """Re-instantiate the class to start the game from the beginning."""
            # Destroy the current instance
            self.root.destroy()  # Close the current Tkinter root window

            # Create a new root window and re-instantiate the HiveGameGUI class
            new_root = tk.Tk()
            new_game = HiveGameGUI(new_root)
            new_root.mainloop()

    def resize_images(self):
        """Resize images to fit inside the hexagon."""
        resized_images = {}
        target_size = int(self.cell_size)
        for name, img in self.original_images.items():
            img_resized = img.resize((target_size, target_size))
            resized_images[name] = ImageTk.PhotoImage(img_resized)
        return resized_images

    def draw_grid(self):
        """Draw hexagonal cells on the grid."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                x_offset = col * self.cell_size * 1.5
                y_offset = row * self.cell_size * math.sqrt(3)
                if col % 2 == 1:
                    y_offset += self.cell_size * math.sqrt(3) / 2

                points = self.hexagon_points(x_offset, y_offset, self.cell_size)
                self.canvas.create_polygon(points, outline="#7f8c8d", fill="#ffffff", width=2, tags=f"cell-{row}-{col}")

                # Draw row and column text (for debugging purposes, you can disable it later)
                text_x = x_offset
                # Adjust the text position slightly above the center
                text_y = y_offset - self.cell_size * 0.5 - 12
                self.canvas.create_text(text_x, text_y, text=f"{row},{col}", fill="black", font=("Segoe UI", 8))

    def hexagon_points(self, x, y, size):
        """Calculate the six corners of a hexagon centered at (x, y)."""
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            points.append(x + size * math.cos(angle))
            points.append(y + size * math.sin(angle))
        return points

    def on_click(self, event):
        """Handle click events to place a piece."""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y)[0]
        tags = self.canvas.gettags(item)

        if not tags or not (tags[0].startswith("cell") or tags[0].startswith("image")):
            return

        row, col = map(int, tags[0].split("-")[1:])

        if self.board[row][col] is None:
            if self.selected_piece_to_move is not None:
                # default on move
                was_moved = self.move_piece(row, col)
                if not was_moved:
                    return
                if self.board[self.selected_piece_coord[0]][self.selected_piece_coord[1]] is None:
                    hexagon_tag = f"cell-{self.selected_piece_coord[0]}-{self.selected_piece_coord[1]}"
                    self.canvas.itemconfig(hexagon_tag, outline=self.colors["None"], width=1)
                self.selected_piece_to_move = None
                self.selected_piece_coord = None

                self.clear_selected_moves(row, col)
                return
            else:
                self.place_piece(row, col)
        else:
            if self.selected_piece_to_move is not None and self.selected_piece_coord == (row, col):
                hexagon_tag = f"cell-{row}-{col}"
                self.canvas.itemconfig(hexagon_tag, outline=self.colors[self.current_player], width=5)
                self.clear_selected_moves(row, col)
                self.selected_piece_coord = None
                self.selected_piece_to_move = None
                return

            if self.selected_piece_to_move is not None and self.selected_piece_to_move[1] == "Beetle":
                was_moved = self.move_piece(row, col)
                # if not was_moved:
                #     return
                hexagon_tag = f"cell-{self.selected_piece_coord[0]}-{self.selected_piece_coord[1]}"
                self.canvas.itemconfig(hexagon_tag, outline=self.colors["None"], width=1)
                self.selected_piece_to_move = None
                self.selected_piece_coord = None

                self.clear_selected_moves(row, col)
                return
            else:
                if isinstance(self.board[row][col], list) and self.current_player == self.board[row][col][-1][0]:
                    self.selected_piece_to_move = self.board[row][col][-1]
                elif self.current_player == self.board[row][col][0]:
                    # Prevent player from selecting a piece before placing bee
                    player_index = 0 if self.current_player == "Player 1" else 1
                    if self.bee_placed[player_index] is False:
                        messagebox.showwarning(
                            "Invalid Move", "You Can't Move pieces before placing your Bee")
                        return
                    # Default on select
                    if self.selected_piece_to_move is not None:
                        selected_row, selected_col = self.selected_piece_coord
                        hexagon_tag = f"cell-{selected_row}-{selected_col}"
                        self.canvas.itemconfig(hexagon_tag, outline=self.colors[self.current_player], width=5)
                        self.clear_selected_moves(row, col)

                    self.selected_piece_to_move = self.board[row][col]
                else:
                    return

                self.selected_piece_coord = (row, col)
                self.selected_piece_valid_moves = self.backend.get_piece_moves(row, col)
                hexagon_tag = f"cell-{row}-{col}"
                self.canvas.itemconfig(hexagon_tag, outline=self.colors["selection"], width=5)

                for [row, col] in self.selected_piece_valid_moves:
                    hexagon_tag = f"cell-{row}-{col}"
                    self.canvas.itemconfig(hexagon_tag, outline=self.colors["moves"], width=5)

                # Update the hexagon outline color and thickness

    def clear_selected_moves(self, row, col):
        for [row, col] in self.selected_piece_valid_moves:
            if not self.backend.boardState.is_cell_occupied(row, col):
                hexagon_tag = f"cell-{row}-{col}"
                self.canvas.itemconfig(
                    hexagon_tag, outline=self.colors["None"], width=1)
            else:
                cell_content = self.board[row][col]
                top_piece = cell_content[-1] if isinstance(cell_content, list) else cell_content

                hexagon_tag = f"cell-{row}-{col}"
                self.canvas.itemconfig(hexagon_tag, outline=self.colors[top_piece[0]], width=5)

        self.selected_piece_valid_moves = None

    def place_piece(self, row, col, piece_type=None):

        character = self.current_character.get()

        if piece_type is not None:
            character = piece_type

        if self.first_play == True:
            row = (int)(self.board_size / 2)
            col = (int)(self.board_size / 2)
            self.first_play = False

        if self.current_player == "Player 1":
            counter = self.turn_counter[0]
        else:
            counter = self.turn_counter[1]

        if counter > 0:
            neighbors = self.backend.boardState.get_neighbors(row, col)
            for neighbor in neighbors:
                # Check if the cell is occupied
                if self.backend.boardState.is_cell_occupied(neighbor[0], neighbor[1]):
                    neighbor_piece = self.board[neighbor[0]][neighbor[1]]

                    if isinstance(neighbor_piece, list):  # If it's a stack
                        top_piece = neighbor_piece[-1]  # Topmost piece
                        owner = top_piece[0]  # Owner of the top piece
                    else:  # Single piece
                        owner = neighbor_piece[0]  # Owner of the single piece

                    # Check ownership
                    if self.current_player != owner:
                        messagebox.showwarning("Invalid Placement", "Can't place piece adjacent to enemy.")
                        return

        # Check if the player still has pieces left
        if self.player_pieces[self.current_player][character] <= 0:
            messagebox.showwarning("No Pieces Left", f"{character} has run out. Please choose a different piece.")
            return

        if not self.backend.is_placement_valid(self.current_player, row, col, character):
            messagebox.showwarning("Invalid Placement", "This move is not valid.")
            return

        if (character == "Bee"):
            if (self.current_player == "Player 1"):
                self.bee_placed[0] = True
                self.bee_coordinates[0] = (row, col)
            else:
                self.bee_placed[1] = True
                self.bee_coordinates[1] = (row, col)

        if (character != "Bee" and self.turn_counter[0] == 3 and self.bee_placed[
            0] is False and self.current_player == "Player 1"):
            messagebox.showwarning("Bee is not placed yet",
                                   "Bee must be placed before the fifth turn. Please place the Bee.")
            return
        elif (character != "Bee" and self.turn_counter[1] == 3 and self.bee_placed[
            1] is False and self.current_player == "Player 2"):
            messagebox.showwarning("Bee is not placed yet",
                                   "Bee must be placed before the fifth turn. Please place the Bee.")
            return

        # Update GUI to reflect the move
        x_offset = col * self.cell_size * 1.5
        y_offset = row * self.cell_size * math.sqrt(3)
        if col % 2 == 1:
            y_offset += self.cell_size * math.sqrt(3) / 2
        image = self.character_images[character]
        self.canvas.create_image(x_offset, y_offset, image=image, tags=f"image-{row}-{col}")

        # Update the hexagon outline color and thickness
        hexagon_tag = f"cell-{row}-{col}"
        self.canvas.itemconfig(hexagon_tag, outline=self.colors[self.current_player], width=5)

        # After successfully placing the piece
        player_index = 0 if self.current_player == "Player 1" else 1
        # self.pieces_on_board[player_index].append((row, col, character))

        # Place piece in the backend
        self.backend.make_move((None, (row, col, character)), self.current_player)

        # Check for game-over conditions
        if self.backend.check_bee_surrounded("Player 1"):
            self.end_game("Player 2 wins!")
        elif self.backend.check_bee_surrounded("Player 2"):
            self.end_game("Player 1 wins!")

        # Update piece count display
        self.piece_count_label.config(text=self.get_piece_count_text())

        # Switch players
        self.switch_player()

    def move_piece(self, row, col, computer_mode=False):

        player_index = 0 if self.current_player == "Player 1" else 1
        if not self.selected_piece_to_move:
            return  # No piece selected to move

        if computer_mode == False and (row, col) not in self.selected_piece_valid_moves:
            messagebox.showwarning("Invalid Move", "Please choose a valid move.")
            return
        if self.current_player == "Player 1":
            if self.bee_placed[0] is False:
                messagebox.showwarning(
                    "Invalid Move", "You Can't Move pieces before placing your Bee")
                hexagon_tag = f"cell-{self.selected_piece_coord[0]}-{self.selected_piece_coord[1]}"
                self.canvas.itemconfig(
                    hexagon_tag, outline=self.colors["Player 1"], width=5)
                self.selected_piece_to_move = None
                self.selected_piece_coord = None
                return
        else:
            if self.bee_placed[1] is False:
                messagebox.showwarning(
                    "Invalid Move", "You Can't Move pieces before placing your Bee")
                hexagon_tag = f"cell-{self.selected_piece_coord[0]}-{self.selected_piece_coord[1]}"
                self.canvas.itemconfig(
                    hexagon_tag, outline=self.colors["Player 2"], width=5)
                self.selected_piece_to_move = None
                self.selected_piece_coord = None
                return

        # Update GUI to reflect the move
        # Retrieve the piece character
        character = self.selected_piece_to_move[1]

        # # Update backend with the move
        # self.board[row][col] = self.selected_piece_to_move

        if character == "Bee":
            self.bee_coordinates[player_index] = (row, col)

        # Handle stacking logic if the target cell is not empty
        if self.board[row][col] is not None:
            if character != "Beetle":
                messagebox.showwarning("Invalid Move", "Only Beetles can move onto occupied cells.")
                return  # Non-Beetle pieces cannot move onto occupied cells
            else:
                # Add the Beetle to the top of the stack
                if isinstance(self.board[row][col], list):

                    self.board[row][col].append(self.selected_piece_to_move)
                else:
                    self.board[row][col] = [self.board[row][col], self.selected_piece_to_move]
                # After successfully placing the piece
                self.pieces_on_board[player_index].append((row, col, character))

        else:
            # Move the piece to an empty cell
            self.board[row][col] = [self.selected_piece_to_move]
            self.pieces_on_board[player_index].append((row, col, character))


        # Remove the piece image from the original position
        self.remove_piece(self.selected_piece_coord[0], self.selected_piece_coord[1])

        # Calculate new position offsets
        x_offset = col * self.cell_size * 1.5
        y_offset = row * self.cell_size * math.sqrt(3)
        if col % 2 == 1:
            y_offset += self.cell_size * math.sqrt(3) / 2
        image = self.character_images[character]
        self.canvas.create_image(x_offset, y_offset, image=image, tags=f"image-{row}-{col}")

        # Update the hexagon outline color and thickness for the new position
        hexagon_tag = f"cell-{row}-{col}"
        self.canvas.itemconfig(hexagon_tag, outline=self.colors[self.current_player], width=5)

        # Check for game-over conditions
        if self.backend.check_bee_surrounded("Player 1"):
            self.end_game("Player 2 wins!")
        elif self.backend.check_bee_surrounded("Player 2"):
            self.end_game("Player 1 wins!")

        self.switch_player()
        return True