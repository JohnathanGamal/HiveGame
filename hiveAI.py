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
