from typing import Optional, List, Tuple

class BoardState:
    def __init__(self, board_size):
        self.board_size: int = board_size
        # Each cell is either None or a Tuple[player: str, piece_type: str]
        self.board: List[List[Optional[Tuple[str, str]]]] = [
            [None for _ in range(board_size)] for _ in range(board_size)
        ]
        self.pieces_on_board = [[], []]
        # TODO (General):
        #   if a player cant place a new piece, pass his role
        #   Add final state -> draw(not just win or lose)


    def get_neighbors(self, row, col):
        """Get the neighbors of a given hex cell."""
        if col % 2 == 0:
            directions = [(-1, 0), (-1, -1), (-1, 1), (0, -1), (1, 0), (0, 1)]
        else:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (1, -1), (1, 1)]
        neighbors = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                neighbors.append((nr, nc))
        return neighbors


    def is_cell_occupied(self, row, col):
        """Check if a cell is occupied by a player's piece."""
        return self.board[row][col] is not None


    def is_hive_intact_after_move(self, origin, destination, piece=None):
        """
        Ensure the hive remains intact after moving or placing a piece.
        Args:
            origin: The original position of the piece (None for placements).
            destination: The target position for the piece.
            piece: The piece being placed (for placements only).
        Returns:
            True if the hive remains intact; False otherwise.
        """
        # Create a simulated list of all pieces on the board
        simulated_pieces_on_board = list(self.pieces_on_board[0] + self.pieces_on_board[1])

        if origin:
            origin_content = self.board[origin[0]][origin[1]]
            if isinstance(origin_content, list):  # Handle stacks
                piece_to_move = origin_content[-1]  # Simulate removing the topmost piece
                if len(origin_content) == 1:
                    simulated_pieces_on_board.remove((origin[0], origin[1], piece_to_move[1]))
            else:
                piece_to_move = origin_content
                simulated_pieces_on_board.remove((origin[0], origin[1], piece_to_move[1]))
        else:
            piece_to_move = piece

        # Simulate placing the piece in the destination
        simulated_pieces_on_board.append((destination[0], destination[1], piece_to_move[1]))

        # If only one piece is on the board, the hive is intact
        if len(simulated_pieces_on_board) == 1:
            return True

        # Start BFS/DFS from any occupied cell
        start = simulated_pieces_on_board[0][:2]  # Use the first piece's coordinates

        visited = set()
        stack = [start]

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                for neighbor in self.get_neighbors(*current):
                    if any(neighbor == (piece[0], piece[1]) for piece in
                            simulated_pieces_on_board) and neighbor not in visited:
                        stack.append(neighbor)

        # Check if all occupied cells are connected
        intact = True
        for piece_info in simulated_pieces_on_board:
            cell_coords = piece_info[:2]
            if cell_coords not in visited:
                intact = False
                break

        return intact