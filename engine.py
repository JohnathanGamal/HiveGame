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


    def is_game_over(self):
        """Check if the game is over."""
        return self.check_bee_surrounded("Player 1") or self.check_bee_surrounded("Player 2")


    def make_move(self, move, player):
        """Make a move on the board."""
        origin, destination = move

        player_index = 0 if player == "Player 1" else 1

        # Handle the case where the piece is not on the board initially
        if origin is not None:
            cell_content = self.boardState.board[origin[0]][origin[1]]
            if isinstance(cell_content, list):
                if len(cell_content) == 1:
                    piece = cell_content[0]
                    self.boardState.board[origin[0]][origin[1]] = None
                else:
                    piece = cell_content.pop(-1)  # Remove the top piece from the stack
            else:
                piece = cell_content
                self.boardState.board[origin[0]][origin[1]] = None  # Remove piece from origin
            self.boardState.pieces_on_board[player_index].remove((origin[0], origin[1], piece[1]))

        else:
            # If origin is None, the piece is being placed for the first time
            piece_type = destination[2]
            piece = (player, piece_type)
            self.player_pieces[player][piece_type] -= 1  # Decrease the piece count

        # Place the piece at the destination
        cell_content = self.boardState.board[destination[0]][destination[1]]
        if isinstance(cell_content, list):
            cell_content.append(piece)  # Add to the stack
        elif cell_content is None:
            self.boardState.board[destination[0]][destination[1]] = piece
        else:
            self.boardState.board[destination[0]][destination[1]] = [cell_content, piece]  # Convert to stack
        self.boardState.pieces_on_board[player_index].append((destination[0], destination[1], piece[1]))


    def undo_move(self, move, player):
        """Undo a move on the board."""
        origin, destination = move
        player_index = 0 if player == "Player 1" else 1

        # Remove the piece from the destination
        cell_content = self.boardState.board[destination[0]][destination[1]]
        if isinstance(cell_content, list):
            piece = cell_content.pop(-1)  # Remove the top piece
            if len(cell_content) == 1:
                self.boardState.board[destination[0]][destination[1]] = cell_content[0]  # Convert to single element
            elif len(cell_content) == 0:
                self.boardState.board[destination[0]][destination[1]] = None
        else:
            piece = cell_content
            self.boardState.board[destination[0]][destination[1]] = None

        # Update pieces_on_board
        self.boardState.pieces_on_board[player_index].remove((destination[0], destination[1], piece[1]))

        # Handle the case where the piece was placed for the first time
        if origin is None:
            # Restore the piece count for the player
            player, piece_type = piece
            self.player_pieces[player][piece_type] += 1
        else:
            # Restore the piece to its origin
            cell_content = self.boardState.board[origin[0]][origin[1]]
            if isinstance(cell_content, list):
                cell_content.append(piece)  # Add to the stack
            elif cell_content is None:
                self.boardState.board[origin[0]][origin[1]] = piece
            else:
                self.boardState.board[origin[0]][origin[1]] = [cell_content, piece]  # Convert to stack

            self.boardState.pieces_on_board[player_index].append((origin[0], origin[1], piece[1]))


    def move_threatens_bee(self, move, opponent):
        """
        Determine if a move threatens the opponent's Bee.
        Args:
            move: A tuple representing the move ((origin_row, origin_col), destination_row, destination_col).
            opponent: The player whose Bee is being threatened.
        Returns:
            True if the move threatens the opponent's Bee, False otherwise.
        """
        origin, destination = move
        if origin is None:
            dest_row, dest_col,_ = destination
        else:
            dest_row,dest_col = destination

        player_index = 0 if opponent == "Player 1" else 1

        # If no Bee is found (error case), we return False
        if not self.bee_placed[player_index]:
            return False

        # Check if the destination is a neighbor of the opponent's Bee
        return (dest_row,dest_col) in self.boardState.get_neighbors(*self.bee_coordinates[player_index])


    def is_move_valid(self, origin, destination):
        """
        Check if a move is valid based on sliding restrictions and hive integrity.
        Args:
            origin: The current position of the piece.
            destination: The target position for the piece.
        Returns:
            True if the move is valid; False otherwise.
        """
        cell_content = self.boardState.board[origin[0]][origin[1]]
        top_piece = cell_content[-1] if isinstance(cell_content, list) else cell_content
        
        if top_piece[1] != "Beetle" and self.boardState.board[destination[0]][destination[1]] is not None:
            return False

        # Check sliding restriction for the origin (exclude the piece itself)
        origin_neighbors = [
            n for n in self.boardState.get_neighbors(*origin)
            if self.boardState.is_cell_occupied(*n) and n != destination
        ]
        if len(origin_neighbors) >= 5:
            return False

        # Check sliding restriction for the destination
        if top_piece[1] != "Grasshopper":
            destination_neighbors = [
                n for n in self.boardState.get_neighbors(*destination)
                if self.boardState.is_cell_occupied(*n) and n != origin
            ]
            if len(destination_neighbors) >= 5:
                return False

        # Check hive integrity after the move
        if not self.boardState.is_hive_intact_after_move(origin, destination):
            return False

        return True
