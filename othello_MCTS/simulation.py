
from othello_MCTS.bitboard import Bitboard, display_bits_in_grid
from othello_MCTS.MCTS import MCTS, Node
import pygame
import numpy as np
from concurrent.futures import ProcessPoolExecutor




def play_match(player1,player2):
    """
    Plays a single match where player1 starts and returns the winner.

    Parameters:
    -----------
    player1 : MCTS or 'user'
        The first player of the match. Can be an instance of the MCTS class or a user input ('user').
    player2 : MCTS or 'user'
        The second player of the match. Can be an instance of the MCTS class or a user input ('user').


    Returns:
    --------
    int
        The winner of the match:
            1 for player1,
            -1 for player2,
            0 for a draw.
    """
    bitboard = Bitboard()

    while bitboard.winner == None:
        play = player1.run_mcts(bitboard.get_state())
        bitboard.play(play)

        if bitboard.winner != None:
            break

        play = player2.run_mcts(bitboard.get_state())
        bitboard.play(play)


    return bitboard.winner

def show_match(player1,player2):
    """
    Plays and displays a single match where player1 starts.

    Parameters:
    -----------
    player1 : MCTS or 'user'
        The first player of the match. Can be an instance of the MCTS class or a user input ('user').
    player2 : MCTS or 'user'
        The second player of the match. Can be an instance of the MCTS class or a user input ('user').
    """
    width = 800
    height = 800
    pygame.init()

    surface = pygame.display.set_mode((width,height))
    bitboard = Bitboard()
    bitboard.show(surface,width,height)
    pygame.display.flip()

    while bitboard.winner == None:
        if player1 == 'user':
            pygame.time.delay(500)
            bitboard.user_move(surface,width,height)
        else:
            play = player1.run_mcts(bitboard.get_state())
            bitboard.play(play)

        bitboard.show(surface,width,height)
        pygame.display.flip()
        pygame.time.delay(100)

        if bitboard.winner != None:
            break

        if player2 == 'user':
            pygame.time.delay(500)
            bitboard.user_move(surface,width,height)
        else:
            play = player2.run_mcts(bitboard.get_state())
            bitboard.play(play)

        bitboard.show(surface,width,height)
        pygame.display.flip()
        pygame.time.delay(100)

    pygame.time.delay(5000)

    

def play_single_match(player1, player2):
    """
    Similar to play_match, but the input parameters are dictionaries specifying player configurations.

    Parameters:
    -----------
    player1 : dict
        Configuration for player1. Includes the following keys:
            max_iter : int 
                Maximum iterations (used only if cap_method == 'iter').
            C : int
                Exploration parameter for MCTS.
            selection_method : str
                Method used for selection ('random' or 'uct').
            player_type : str
                Type of the player ('MCTS' or 'random').
            iterations_per_simulation : int
                Number of simulations per iteration.
            max_runtime : int
                Maximum runtime allowed for the simulation (in seconds, used only if cap_method == 'time').
            cap_method : str
                Method to cap the simulation ('iter' or 'time').
    player2 : dict
        Same as player1, but for player2.

    Returns:
    --------
    int
        The winner of the match:
            1 for player1,
            -1 for player2,
            0 for a draw.
    """

    return play_match(MCTS(**player1), MCTS(**player2))



def tournament(players):
    """
    Runs a tournament between multiple players, simulating 10 matches in parallel, and saves the results.

    Parameters:
    -----------
    players : list of dict
        A list of player configurations, where each configuration is a dictionary containing parameters such as:
            max_iter : int
                Maximum iterations (used only if cap_method == 'iter').
            C : int
                Exploration parameter for MCTS.
            selection_method : str
                Method used for selection ('random' or 'uct').
            player_type : str
                Type of the player ('MCTS').
            iterations_per_simulation : int
                Number of simulations per iteration.
            max_runtime : int
                Maximum runtime allowed for the simulation (in seconds, used only if cap_method == 'time').
            cap_method : str
                Method to cap the simulation ('iter' or 'time').

    Returns:
    --------
    None

    Notes:
    ------
    - Simulates 10 matches between each ordered pair of players in the list, meaning each player gets to be player1 and player2 against every other player.
    - Aggregates the results as:
        - `wins_player1[i, j]`: Number of wins for player1 when matched against player2.
        - `wins_player2[i, j]`: Number of wins for player2 when matched against player1.
        - `draws[i, j]`: Number of matches that ended in a draw between player1 and player2.
    - Saves results in both `.npy` (binary) and `.txt` (readable) formats:
        - `wins_player1.npy` / `wins_player1.txt`
        - `wins_player2.npy` / `wins_player2.txt`
        - `draws.npy` / `draws.txt`
    """
    wins_player1 = np.zeros((len(players), len(players)))
    wins_player2 = np.zeros((len(players), len(players)))
    draws = np.zeros((len(players), len(players)))

    # Use ProcessPoolExecutor for parallel execution
    with ProcessPoolExecutor() as executor:
        for i, player1 in enumerate(players):
            for j, player2 in enumerate(players):
                # Run 10 matches in parallel
                futures = [executor.submit(play_single_match, player1, player2) for _ in range(10)]
                results = [future.result() for future in futures]
                # Aggregate results
                wins_player1[i, j] = results.count(1)  # Player 1 wins
                wins_player2[i, j] = results.count(-1)  # Player 2 wins
                draws[i,j] = results.count(0)



                print(f"{i * len(players) + j + 1} out of {len(players) ** 2}")

    # Save results
    np.save('wins_player1.npy', wins_player1)
    np.savetxt('wins_player1.txt', wins_player1)
    np.save('wins_player2.npy', wins_player2)
    np.savetxt('wins_player2.txt', wins_player2)
    np.save('draws.npy', draws)
    np.savetxt('draws.txt', draws)