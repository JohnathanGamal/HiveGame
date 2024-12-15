class Pieces:
    @staticmethod
    def get_bee_moves(boardState, row, col):
        """Bee moves to any unoccupied neighboring cell while keeping the hive intact."""
        valid_moves = []
        for neighbor in boardState.get_neighbors(row, col):
            if not boardState.is_cell_occupied(*neighbor) and boardState.is_hive_intact_after_move((row, col), neighbor):
                valid_moves.append(neighbor)
        return valid_moves


    @staticmethod
    def get_ant_moves(boardState, row, col):
        """Ant can move to any unoccupied cell while keeping the hive intact."""
        visited = set()
        stack = [(row, col)]  # Start from the Ant's position
        valid_moves = []

        while stack:
            current = stack.pop()
            for neighbor in boardState.get_neighbors(*current):
                if neighbor not in visited and not boardState.is_cell_occupied(*neighbor):
                    visited.add(neighbor)
                    if boardState.is_hive_intact_after_move((row, col), neighbor):
                        valid_moves.append(neighbor)
                    stack.append(neighbor)  # Keep exploring
        return valid_moves


    @staticmethod
    def get_spider_moves(boardState, row, col):
        """Spider moves exactly 3 spaces, no revisits, keeping the hive intact."""
        valid_moves = set()  # Use a set to prevent duplicate moves

        def dfs(current, path):
            if len(path) == 4:  # Exactly 3 moves (path includes starting cell)
                # Check hive integrity only for the final position
                if boardState.is_hive_intact_after_move((row, col), path[-1]):
                        valid_moves.add(path[-1])  # Add the final position to the set
                return
            for neighbor in boardState.get_neighbors(*current):
                if neighbor not in path and not boardState.is_cell_occupied(*neighbor):  # Valid move
                    dfs(neighbor, path + [neighbor])

        dfs((row, col), [(row, col)])
        return list(valid_moves)  # Convert the set to a list before returning


    @staticmethod
    def get_beetle_moves(boardState, row, col):
        """Beetle moves 1 space to any adjacent cell (occupied or unoccupied), keeping the hive intact."""
        valid_moves = []
        for neighbor in boardState.get_neighbors(row, col):
            if boardState.is_hive_intact_after_move((row, col), neighbor):  # Hive integrity check
                valid_moves.append(neighbor)
        return valid_moves


    @staticmethod
    def get_grasshopper_moves(boardState, row, col):
        """Grasshopper jumps in a straight line over adjacent pieces to the first empty cell."""
        valid_moves = []

        # Define directions for even and odd columns
        even_directions = [(-1, 0), (1, 0), (-1, -1), (-1, 1), (0, -1), (0, 1)]
        odd_directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]

        # Choose initial directions based on the starting column's parity
        directions = even_directions if col % 2 == 0 else odd_directions

        for idx, (dr, dc) in enumerate(directions):
            r, c = row + dr, col + dc  # Move to the first adjacent cell
            jumped = False  # Indicates whether the grasshopper has jumped over at least one piece

            while True:
            # Determine the current column's direction set
                current_directions = even_directions if c % 2 == 0 else odd_directions
                dr, dc = current_directions[idx]  # Maintain consistent direction

                if not boardState.is_cell_occupied(r, c):
                    if jumped:  # Can land only if it's after a jump
                        if boardState.is_hive_intact_after_move((row, col), (r, c)):  # Check hive integrity
                            valid_moves.append((r, c))  # Add valid move
                    break
                else:
                    jumped = True  # Grasshopper jumps over this piece

                # Move further in the same direction
                r += dr
                c += dc

        return valid_moves
