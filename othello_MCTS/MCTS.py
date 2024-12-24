import copy
from othello_MCTS.bitboard import Bitboard
import random
import time
from math import *


class Node:
    """
    Represents a node in the Monte Carlo Tree Search.

    Attributes:
    -----------
    move : int
        The move associated with this node.
    parent : Node
        The parent node in the search tree.
    value : float
        The total value accumulated from simulations.
    uct : float
        The Upper Confidence Bound for Trees (UCT) value for this node.
    n_visits : int
        The number of times this node has been visited.
    c : float
        Exploration parameter for UCT calculation.
    children : dict
        A dictionary of child nodes indexed by their moves.
    """
    def __init__(self, move, parent, C = 10):
        self.parent = parent
        self.move = move
        self.value = 0
        self.uct = 0
        self.n_visits = 0
        self.c = C
        self.children = {}


    def set_uct(self):
        """
        Calculates and updates the UCT value of the node.
        """
        if self.n_visits == 0:
            self.uct = float('inf')
            return
        self.uct = self.value/self.n_visits + self.c*sqrt(log(self.parent.n_visits)/self.n_visits)



class MCTS:
    """
    Implements the Monte Carlo Tree Search algorithm.

    Attributes:
    -----------
    max_iter : int
        Maximum number of iterations for the algorithm.
    C : float
        Exploration parameter for UCT calculation.
    selection_method : str
        Strategy for node selection ('uct' or 'random').
    player_type : str
        Type of player ('MCTS' or 'random').
    iterations_per_simulation : int
        Number of rollouts per simulation.
    runtime : float
        Maximum allowed runtime for the algorithm.
    cap_method : str
        Termination criteria ('time' or 'iter').
    root_state : tuple
        The state of the game at the root node.
    main_player : int
        The player for whom the MCTS is being run.
    root : Node
        The root node of the search tree.
    run_time : float
        Time spent running the algorithm.
    node_count : int
        Number of nodes generated during the search.
    num_rollouts : int
        Total number of rollouts performed.
    bitboard : Bitboard
        The bitboard representing the game state.

    Methods:
    --------
    run_mcts(state):
        Executes the MCTS algorithm to determine the best move.

    select():
        Selects a node to expand based on the selection strategy.

    expand(parent):
        Expands a node by generating its children.

    run_simulation():
        Runs a simulation from the current state and returns the resulting value.

    back_propagate(node, value):
        Propagates simulation results up the tree.

    best_move():
        Determines the best move based on child node values.

    reset():
        Resets the MCTS instance to its initial state.
    """

    def __init__(self, max_iter = 100, C = 10, selection_method = 'random', player_type = 'MCTS', 
                 iterations_per_simulation = 1, runtime = 5, cap_method = 'iter'):

        self.root_state = None
        self.main_player = None
        self.c = C
        self.root = Node(None, None, C = self.c)
        self.run_time = 0
        self.max_runtime = runtime
        self.node_count = 1
        self.num_rollouts = 0
        self.bitboard = Bitboard()
        self.max_iter = max_iter
        self.selection_method = selection_method
        self.player_type = player_type
        self.iterations_per_simulation = iterations_per_simulation
        self.cap_method = cap_method

    def run_mcts(self, state):
        """
        Executes the Monte Carlo Tree Search algorithm to determine the best move.

        Parameters:
        -----------
        state : tuple
            The initial game state for the MCTS.

        Returns:
        --------
        int
            The best move determined by the MCTS algorithm.
        """
        
        if self.player_type =='random':
            _,_,moves = self.bitboard.get_moves()
            moves = [i for i in range(moves.bit_length()) if (moves >> i) & 1]
            return random.choice(moves)


        self.reset()
        self.root_state = copy.deepcopy(state)
        self.bitboard.set_state(state)
        self.main_player = state[1]

        start_time = time.time()

        if self.cap_method == 'time':
        
            while time.time() - start_time < self.max_runtime:
                node = self.select()
                value = self.run_simulation()
                self.back_propagate(node,value)
                self.num_rollouts += self.iterations_per_simulation
        
            self.run_time = time.time() - start_time
            return self.best_move()

        if self.cap_method == 'iter':

            for _ in range(self.max_iter):
                node = self.select()
                value = self.run_simulation()
                self.back_propagate(node,value)
                self.num_rollouts += self.iterations_per_simulation
        
            self.run_time = time.time() - start_time
            return self.best_move()


    def select(self):
        """
        Traverses the tree to select a promising node based on the chosen selection strategy.

        Returns:
        --------
        Node
            The selected node for expansion or simulation.
        """
        self.bitboard.reset()
        self.bitboard.set_state(self.root_state)

        node = self.root

        while len(node.children) != 0:

            if self.selection_method == 'uct':
                children = node.children.values()
                list(map(lambda x: x.set_uct(),children))
                max_value = max([child.uct for child in children])
                max_nodes = [child for child in children if child.uct == max_value]

                node = random.choice(max_nodes)

            if self.selection_method == 'random':
                node = random.choice(list(node.children.values()))

            self.bitboard.play(node.move)

            if node.n_visits == 0:
                return node

        if self.expand(node):
            node = random.choice(list(node.children.values()))
            self.bitboard.play(node.move)

        return node


    def expand(self, parent):
        """
        Expands a node by generating all possible moves as its children.

        Parameters:
        -----------
        parent : Node
            The parent node to expand.

        Returns:
        --------
        bool
            True if the node was successfully expanded, False if no moves are possible.
        """
        if self.bitboard.winner != None:
            return False

        _,_,moves = self.bitboard.get_moves()
        moves = [i for i in range(moves.bit_length()) if (moves >> i) & 1]
        parent.children = {move: Node(move, parent, C = self.c) for move in moves}
        self.node_count += len(parent.children)

        return True

    def run_simulation(self):
        """
        Runs a simulated game from the current state to estimate the value of a node.

        Returns:
        --------
        float
            The accumulated value from the simulation.
        """
        value = 0
        state = self.bitboard.get_state()

        if self.bitboard.winner != None:
            value = self.iterations_per_simulation*((self.main_player*self.bitboard.winner + 1)/2)**3
            return value

        for _ in range(self.iterations_per_simulation):

            self.bitboard.reset()
            self.bitboard.set_state(state)

            while self.bitboard.winner == None:
                self.bitboard.play(72)
            value += ((self.main_player*self.bitboard.winner + 1)/2)**3            

        return value

    def back_propagate(self, node, value):
        """
        Propagates the simulation results up the tree, updating values and visit counts.

        Parameters:
        -----------
        node : Node
            The node from which backpropagation starts.
        value : float
            The value to propagate up the tree.
        """
        while True:
            node.n_visits += self.iterations_per_simulation
            node.value += value
            if node.parent == None:
                break
            node = node.parent

    def best_move(self):
        """
        Determines the best move by selecting the child node with the highest accumulated value.

        Returns:
        --------
        int
            The move corresponding to the best child node.
        """
        max_value = max([child.value for child in self.root.children.values()])
        max_moves = [move for move in self.root.children.keys() if self.root.children[move].value == max_value]
        return random.choice(max_moves)

    def reset(self):
        """
        Resets the MCTS instance to its initial state, clearing the tree and other attributes.
        """
        self.root_state = None
        self.main_player = None
        self.root = Node(None, None)
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0
        self.bitboard.reset()
