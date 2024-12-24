# othello with Bitboard Representation and MCTS

***This project follows the same structure as my Connect4 project, with the only significant difference being the bitboard implementation tailored for Othello.***

This project implements a othello game using a bitboard representation for efficient game state management. The AI for the game is built using the Monte Carlo Tree Search (MCTS) algorithm. The repository is structured to allow for easy experimentation and includes features for running matches, visualizing gameplay, and conducting tournaments.

---
## Table of Contents

## Features

- **Bitboard Representation**: Efficiently encodes game states using binary operations.
- **Monte Carlo Tree Search (MCTS)**: Implements an AI player for Othello.
- **Game Visualization**: Uses Pygame to display the Othello grid and gameplay.
- **Tournament Simulation**: Allows multiple AI configurations to compete against each other.
- **Parallel Execution**: Leverages Python's `concurrent.futures` for running matches in parallel.

---

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/beloof/othello_MCTS
   ```
2. Install dependencies:
   ```
   cd othello_MCTS
   pip install .
   ```

---

## Usage

### Running a Match
To play a single match between two AI players:
```
from othello_MCTS import show_match
show_match(MCTS(), MCTS())
```

### Tournament Simulation
To run a tournament among multiple AI configurations:
```
from othello_MCTS import tournament

params_list = [
    {
        'selection_method': 'random',
        'iterations_per_simulation': 1,
        'runtime': 5,
        'cap_method': 'time'
    },
    {
        'selection_method': 'uct',
        'iterations_per_simulation': 100,
        'runtime': 10,
        'cap_method': 'iterations'
    }
]

tournement(params_list)
```

### Visualizing Matches
To visualize gameplay between two AI players:
```
from othello_MCTS import show_match, MCTS
show_match(MCTS(),MCTS())
```
![image](/images/Screenshot.png)
---

## File Structure

```
.
├── othello_MCTS/
│   ├── __init__.py          
│   ├── bitboard.py          # Bitboard implementation for Othello
│   ├── simulation.py        # basic funstions to show/play matches
│   └── MCTS.py              # MCTS algorithm implementation
├── docs/                    # html documentation
├── images/                  # readme image
├── main.py                  # Main script for running matches and tournaments
├── setup.py                 # Python setup file
└── README.md                # Documentation
```

---

## How It Works

### Bitboard Representation
The game board is represented as a 8x8 grid encoded into a 72-bit integer for each player. Binary operations are used to calculate valid moves, check for wins, and update game states efficiently.

The positions on the board are as follows:
```
.   .   .   .   .   .   .   .
7  16  25  34  43  52  61  70
6  15  24  33  42  51  60  69
5  14  23  32  41  50  59  68
4  13  22  31  40  49  58  67
3  12  21  30  39  48  57  66
2  11  20  29  38  47  56  65
1  10  19  28  37  46  55  64
0   9  18  27  36  45  54  63
```

check [this](http://blog.gamesolver.org/solving-connect-four/06-bitboard/) for more detail
### Monte Carlo Tree Search (MCTS)
The MCTS algorithm uses the following steps to determine the best move:
1. **Selection**: Traverses the game tree using a selection strategy (e.g., UCT).
2. **Expansion**: Adds a new node to the tree.
3. **Simulation**: Simulates random playouts from the new node.
4. **Backpropagation**: Updates the node values based on the simulation outcomes.

### Tournament Simulation
A tournament is run by pairing different AI configurations and letting them play multiple matches. Results are saved in `.npy` and `.txt` formats for analysis.

---

## Dependencies

- `pygame`
- `numpy`
- `matplotlib`

Install dependencies using:
```
pip install .
```
---
## Documentation

Full documentation [here](https://github.com/beloof/connect4_MCTS/tree/master/docs/build/html)
 
---

## Future Work
- Add a human vs. AI mode.
- Implement advanced heuristics for MCTS simulations.
- Enhance visualization with real-time statistics.
- Optimize bitboard operations for larger grids.
---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgments
Special thanks to [PascalPons](http://blog.gamesolver.org/solving-connect-four/06-bitboard/) and [Qi Wang](https://www.harrycodes.com/blog/monte-carlo-tree-search) for sharing insights

