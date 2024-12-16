from board import BoardState
from pieces import Pieces


class HiveGame:
    def __init__(self, board_size: int):
        self.boardState = BoardState(board_size)

        self.first_play = True
        self.current_player = "Player 1"
        self.turn_counter = [0, 0]
        self.bee_placed = [False, False]
        self.bee_coordinates = [None, None]
        self.player_pieces = {
            "Player 1": {"Bee": 1, "Ant": 3, "Spider": 2, "Grasshopper": 3, "Beetle": 2},
            "Player 2": {"Bee": 1, "Ant": 3, "Spider": 2, "Grasshopper": 3, "Beetle": 2}
        }


    def get_piece_moves(self, row, col):
        """
        Get valid moves for a specific piece at a given position.
        """
        piece = self.boardState.board[row][col]
        if isinstance(piece, list):
            piece = piece[-1]
        if not piece:  # No piece at the position
            return []

        _, piece_type = piece
        moves = []

        if piece_type == "Bee":
            possible_moves = Pieces.get_bee_moves(self.boardState, row, col)
        elif piece_type == "Ant":
            possible_moves = Pieces.get_ant_moves(self.boardState, row, col)
        elif piece_type == "Spider":
            possible_moves = Pieces.get_spider_moves(self.boardState, row, col)
        elif piece_type == "Beetle":
            possible_moves = Pieces.get_beetle_moves(self.boardState, row, col)
        elif piece_type == "Grasshopper":
            possible_moves = Pieces.get_grasshopper_moves(self.boardState, row, col)
        else:
            return []

        # Validate all possible moves
        for move in possible_moves:
            if self.is_move_valid((row, col), move):
                moves.append(move)

        return moves


    def check_bee_surrounded(self, player):
        """Check if a player's Bee is surrounded."""
        # Retrieve the bee's coordinates directly
        player_index = 0 if player == "Player 1" else 1
        if self.bee_placed[player_index]:
            row, col = self.bee_coordinates[player_index]
            # Check all neighbors; if any are empty, the Bee is not surrounded
            return all(self.boardState.is_cell_occupied(r, c) for r, c in self.boardState.get_neighbors(row, col))
        return False


    def is_placement_valid(self, player, row, col, piece):
        """
        Check if placing a piece is valid at the given position.
        Placement is invalid if:
        - The player has a piece.
        - The position is not empty.
        - The Queen Bee has not been placed by the 4th turn (if required).
        - The position is adjacent to opponent pieces (except during turn 0).
        - The hive would break after placement.
        """
        # Check if the player still has pieces left
        if self.player_pieces[player][piece] <= 0:
            return False

        # Ensure the cell is empty
        if self.boardState.board[row][col] is not None:
            return False

        # Temporarily place the piece to check hive integrity
        self.boardState.board[row][col] = (player, piece)  # Simulate placement
        is_intact = self.boardState.is_hive_intact_after_move(None, (row, col), piece)
        self.boardState.board[row][col] = None  # Revert placement

        if not is_intact:
            return False  # Hive would break with this placement

        # Allow adjacency to opponent pieces during turn 0
        player_index = 0 if player == "Player 1" else 1
        if self.turn_counter[player_index] == 0:
            return True  # Turn 0 allows placement anywhere valid if hive is intact

        # Check adjacency rules
        neighbors = self.boardState.get_neighbors(row, col)
        for neighbor in neighbors:
            if self.boardState.is_cell_occupied(neighbor[0], neighbor[1]):
                neighbor_piece = self.boardState.board[neighbor[0]][neighbor[1]]

                if isinstance(neighbor_piece, list):  # If it's a stack
                    top_piece = neighbor_piece[-1]  # Topmost piece
                    owner = top_piece[0]  # Owner of the top piece
                else:  # Single piece
                    owner = neighbor_piece[0]

                if owner != player:
                    return False  # Adjacent to an opponent's piece (invalid)

        # Bee placement rule: Must be placed by the 4th turn
        if self.turn_counter[player_index] >= 3 and not self.bee_placed[player_index]:
            return piece == "Bee"  # Only the Bee can be placed after the 3rd turn if not already placed


        # Valid if adjacent to friendly pieces
        return True


    def is_on_top_of_stack(self, piece, row, col):
        """
        Check if the given piece is on top of the stack at the specified cell.

        :param piece: Tuple representing the piece (player, character).
        :param row: Row index of the cell.
        :param col: Column index of the cell.
        :return: True if the piece is on top or the only piece in the cell, False otherwise.
        """
        cell_content = self.boardState.board[row][col]

        if isinstance(cell_content, list):
            # If it's a stack, check if the top piece matches the given piece
            return cell_content[-1] == piece
        elif cell_content is None:
            # If the cell is empty, return False
            return False
        else:
            # If it's a single piece, check if it matches the given piece
            return cell_content == piece


