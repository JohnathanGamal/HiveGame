import time

from engine import HiveGame

class HiveAI:

    def __init__(self, engine: HiveGame):
        self.engine = engine


    def minimax(self, depth, is_maximizing_player):
        """
        Minimax algorithm without pruning.
        Args:
            depth: The remaining depth to search.
            is_maximizing_player: True if it's the maximizing player's turn.
        Returns:
            The evaluation score of the best move for the current player.
        """
        if depth == 0 or self.engine.is_game_over():
            return self.evaluate_board()

        player_index = 0 if is_maximizing_player else 1
        self.engine.turn_counter[player_index] += 1  # Increment turn counter

        if is_maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_moves("Player 1"):
                self.engine.make_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                eval = self.minimax(depth - 1, False)
                self.engine.undo_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                max_eval = max(max_eval, eval)
            self.engine.turn_counter[player_index] -= 1  # Decrement turn counter
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_moves("Player 2"):
                self.engine.make_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                eval = self.minimax(depth - 1, True)
                self.engine.undo_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                min_eval = min(min_eval, eval)
            self.engine.turn_counter[player_index] -= 1  # Decrement turn counter
            return min_eval


    def alpha_beta(self, depth, is_maximizing_player, alpha=float('-inf'), beta=float('inf')):
        """
        Minimax algorithm with Alpha-Beta Pruning.
        Args:
            depth: The remaining depth to search.
            is_maximizing_player: True if it's the maximizing player's turn.
            alpha: The best value the maximizing player can guarantee so far.
            beta: The best value the minimizing player can guarantee so far.
        Returns:
            The evaluation score of the best move for the current player.
        """
        if depth == 0 or self.engine.is_game_over():
            eval = self.evaluate_board()
            return eval

        player_index = 0 if is_maximizing_player else 1
        self.engine.turn_counter[player_index] += 1  # Increment turn counter

        if is_maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_moves("Player 1"):
                self.engine.make_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                eval = self.alpha_beta(depth - 1, False, alpha, beta)
                self.engine.undo_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha:  # Beta cut-off
                    break
            self.engine.turn_counter[player_index] -= 1  # Decrement turn counter
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_moves("Player 2"):
                self.engine.make_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                eval = self.alpha_beta(depth - 1, True, alpha, beta)
                self.engine.undo_move(
                    move, "Player 1" if is_maximizing_player else "Player 2")
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha:  # Alpha cut-off
                    break
            self.engine.turn_counter[player_index] -= 1  # Decrement turn counter
            return min_eval


    def iterative_deepening(self, is_maximizing_player, max_depth, time_limit):
        start_time = time.time()
        best_move = None

        for depth in range(1, max_depth + 1):
            # Check if time is up
            if time.time() - start_time >= time_limit:
                break

            # Track if the depth was fully evaluated
            fully_evaluated = True

            # Find the best move for the current depth
            current_move, fully_evaluated = self.find_best_move(depth, is_maximizing_player, start_time, time_limit)

            # Update the best move only if the depth was fully evaluated
            if (fully_evaluated or depth == 1) and current_move is not None:
                best_move = current_move

        return best_move


    def evaluate_board(self):
        """
        Evaluate the board state and assign a score to determine which player has the advantage.
        Positive scores favor Player 1; negative scores favor Player 2.
        Returns:
            int: The evaluation score.
        """
        score = 0

        # Weight constants for evaluation criteria
        THREAT_WEIGHT = 800
        MOBILITY_WEIGHT = 5
        PIECE_COUNT_WEIGHT = 3

        if self.engine.check_bee_surrounded("Player 1"):
            score -= 10000  # Heavy penalty if Player 1's Bee is surrounded
        if self.engine.check_bee_surrounded("Player 2"):
            score += 10000  # Reward if Player 2's Bee is surrounded

        # Evaluate each player
        for player in ["Player 1", "Player 2"]:
            opponent = "Player 2" if player == "Player 1" else "Player 1"
            multiplier = 1 if player == "Player 1" else -1

            # Queen (Bee) Threat
            bee_threat = self.get_bee_threat(opponent)
            score += multiplier * bee_threat * THREAT_WEIGHT

            # Mobility
            all_moves = self.get_all_moves(player)
            score += multiplier * len(all_moves) * MOBILITY_WEIGHT

            # Piece Count
            piece_count = self.count_pieces(player)
            score += multiplier * piece_count * PIECE_COUNT_WEIGHT

        return score


    def get_bee_threat(self, player):
        """Count how many neighbors surround the Bee for the given player."""
        # Retrieve the bee's coordinates directly
        player_index = 0 if player == "Player 1" else 1
        if self.engine.bee_placed[player_index]:
            row, col = self.engine.bee_coordinates[player_index]
            neighbors = self.engine.boardState.get_neighbors(row, col)  # Get all neighbor positions
            occupied_count = 0  # Initialize the counter

            for r, c in neighbors:
                if self.engine.boardState.is_cell_occupied(r, c):  # Check if the neighbor is occupied
                    occupied_count += 1  # Increment the counter
            return occupied_count
        return 0


    def count_pieces(self, player):
        """Count the number of pieces for the given player."""
        player_index = 0 if player == "Player 1" else 1
        return len(self.engine.boardState.pieces_on_board[player_index])


    def get_all_empty_neighbors(self):
        """Get all empty neighbors around the hive."""
        empty_neighbors = set()
        for player_pieces in self.engine.boardState.pieces_on_board:
            for row, col, _ in player_pieces:
                for neighbor in self.engine.boardState.get_neighbors(row, col):
                    if self.engine.boardState.board[neighbor[0]][neighbor[1]] is None:
                        empty_neighbors.add(neighbor)
        return empty_neighbors


    def get_all_moves(self, player):
        """Get all possible moves for a given player."""
        all_moves = []
        player_index = 0 if player == "Player 1" else 1

        # If the Bee hasn't been placed, restrict to placement moves only
        if not self.engine.bee_placed[player_index]:
            if self.engine.turn_counter[player_index] >= 3:
                for neighbor in self.get_all_empty_neighbors():
                    row, col = neighbor
                    if self.engine.is_placement_valid(player, row, col, "Bee"):
                        all_moves.append((None, (row, col, "Bee")))
            else:
                if self.engine.turn_counter[0] == 0 and self.engine.turn_counter[1] == 0:
                    # Define the center of the board
                    center_row = (int)(self.engine.boardState.board_size / 2)
                    center_col = (int)(self.engine.boardState.board_size / 2)
                    for piece, count in self.engine.player_pieces[player].items():
                        if count > 0:  # Only consider pieces still in hand
                            if self.engine.is_placement_valid(player, center_row, center_col, piece):
                                all_moves.append((None, (center_row, center_col, piece)))
                else:
                    for piece, count in self.engine.player_pieces[player].items():
                        if count > 0:  # Only consider pieces still in hand
                            for neighbor in self.get_all_empty_neighbors():
                                row, col = neighbor
                                if self.engine.is_placement_valid(player, row, col, piece):
                                    all_moves.append((None, (row, col, piece)))  # (None, (placement info))
            return all_moves

        # Generate moves for pieces already on the board (if the Bee is placed)
        for row, col, piece_character in self.engine.boardState.pieces_on_board[player_index]:
            cell_content = self.engine.boardState.board[row][col]
            top_piece = cell_content[-1] if isinstance(cell_content, list) else cell_content

            # Ensure both player and character match
            if top_piece == (player, piece_character) and self.engine.is_on_top_of_stack(top_piece, row, col):
                piece_moves = self.engine.get_piece_moves(row, col)
                for move in piece_moves:
                    all_moves.append(((row, col), move))

        # Add placement moves for remaining pieces in hand
        for piece, count in self.engine.player_pieces[player].items():
            if count > 0:  # Only consider pieces still in hand
                for neighbor in self.get_all_empty_neighbors():
                    row, col = neighbor
                    if self.engine.is_placement_valid(player, row, col, piece):
                        all_moves.append((None, (row, col, piece)))  # (None, (placement info))

        return all_moves


    def find_best_move(self, depth, is_maximizing_player, start_time, time_limit):
        best_eval = float('-inf') if is_maximizing_player else float('inf')
        best_move = None

        player = "Player 1" if is_maximizing_player else "Player 2"
        player_index = 0 if is_maximizing_player else 1

        moves = self.get_all_moves(player)
        fully_evaluated = True  # Assume the depth will be fully evaluated

        for move in moves:
            # Check timeout before making a move
            if time.time() - start_time >= time_limit and depth > 1:
                fully_evaluated = False  # Mark the depth as not fully evaluated
                break

            # Simulate the move
            self.engine.make_move(move, player)
            self.engine.turn_counter[player_index] += 1
            # Recursively evaluate using alpha-beta pruning
            eval = self.alpha_beta(depth - 1, not is_maximizing_player, alpha=float('-inf'), beta=float('inf'))

            # Undo the move
            self.engine.undo_move(move, player)
            self.engine.turn_counter[player_index] -= 1

            # Update the best move and evaluation
            if (is_maximizing_player and eval > best_eval) or (not is_maximizing_player and eval < best_eval):
                best_eval = eval
                best_move = move
        return best_move, fully_evaluated
