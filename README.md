# Hive Game AI Project
A project for our `CSE 472s: ARTIFICIAL INTELLIGENCE` course, focused on implementing AI algorithms and studying game-playing strategies.

## Game Overview
Hive is a two-player strategy game played on any flat surface without a board. The game consists of 22 pieces: 11 black and 11 white, each resembling creatures with unique movement patterns.

The game begins when the first piece is placed, and subsequent pieces form the playing area. The objective is to completely surround your opponent's Queen Bee while preventing your own Queen Bee from being surrounded. The player who surrounds the opponent's Queen Bee first wins the game.

This project aims to study AI game-playing algorithms like `Minimax` and `Alpha-Beta Pruning` by recreating the Hive game, allowing players to compete against each other or against our internally developed AI system.


## Project documents

- [Report link](https://docs.google.com/document/d/1x2XxNLScSTTDHhFSzYN4qggKg_jJV0k8jCkGaN62ES4/edit?usp=sharing)  – Detailed project report.

- [Video link](https://www.youtube.com/watch?v=zbcmykzmZIE&feature=youtu.be) – Project demonstration video.

## Installation and Setup

1. **Clone the repository and navigate into the project directory**:
   ```bash
   git clone https://github.com/JohnathanGamal/HiveGame.git
   cd HiveGame
   ```

2. **Create and activate the virtual environment**:  
   - On **Unix/macOS**:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     python -m venv .venv
     .\.venv\Scripts\activate
     ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Check that everything is working correctly**:
   ```bash
   python gui.py    # Should launch the game interface
   ```

## Project Overview

The HIVE AI project involves two major components: the `frontend` and the `backend`. 
The project is divided into two major components:
- Frontend
- Backend

### The frontend

Responsible for the user interface, including game board display, player interactions, and game modes.

The GUI uses a hexagonal coordinate system to display the game board, allowing piece selection and previewing possible moves for each piece.

#### Game modes

We support the following game modes:
- **Player vs. Player (PvP):** Two human players take turns interacting with the board.
- **Player vs. Computer (PvC):** A human player competes against an AI opponent.
- **Computer vs. Computer (CvC):** Two AI players compete, showcasing the AI algorithms' capabilities.

#### Game difficulties

We support the following game difficulties:
- **Easy:** The AI makes simpler decisions with fewer moves, suitable for beginners.
- **Medium:** The AI evaluates more moves for moderate competition.
- **Hard:** The AI explores deeper moves and given more time for a highly competitive experience.

### The backend

The backend component handles the core game logic including:
- Game state management
- Rule enforcement
- AI decision-making

#### Game state management

- Internally, the game is represented as a 2D-array of stacks to accomodate for multiple pieces being on top of each other.
- Pieces available to every player and pieces on the board are represented by an array that stores the count of the pieces left or the locaation of the player's piece on the board respectively.

#### Rule enforcement

The game supports the rules of the vanila hive board game described by this [document](https://www.ultraboardgames.com/hive/game-rules.php)

The pieces available to each player are:
- 1 Queen Bee (Yellow-Gold)
- 2 Spiders (Brown)
- 2 Beetles (Purple)
- 3 Grasshoppers (Green)
- 3 Soldier Ants (Red)

Rules are enforced by either generating moves that conform with these rules or by checking whether the players move action is valid against these rules

#### AI decision-making

##### Heuristics:

1. `Queen Bee Surrounding Heuristic:`
Prioritizes moves that surround the opponent’s Queen Bee and prevent the player's from being surrounded. Winning moves are highly valued.

2. `Piece Movement Heuristic:`
High mobility provides more options, allowing offensive, defensive, and reactive strategies for board control.

3. `Pieces Weights Heuristic:`
Pieces are valued based on mobility and strategic importance. More mobile pieces, like Soldier Ants, are prioritized.

##### Algorithms:

- `Minimax algorithm:`
drives the AI’s decision-making by evaluating all possible moves while evaluating its values by certain heuristics and selecting the best move. 

- `Alpha-Beta Pruning:`
an enhancment over the `Minimax algorithm` which improves efficiency by reducing the number of nodes evaluated if no more gain can be achieved by exploring this move, focusing on more promising paths.

- `Iterative Deepening`
used to balance performance and computational constraints. It incrementally increases search depth, ensuring the best move is found within a certain time limit. `Alpha-Beta pruning` is incorporated within iterative deepening for optimal efficiency. This also helps adjust difficulty by controlling the search depth or time limit.
