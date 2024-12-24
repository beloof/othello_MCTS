import random
from functools import reduce
import pygame
import copy


class Bitboard:
    """
    A class to represent a game board using bitboards for efficient game state representation and manipulation.
    
    Attributes:
    -----------
    player_bitboards : list
        A list representing the bitboards for the two players. Index 1 represents one player, and index -1 the other.
    colors : list
        A list of colors for representing the board and players visually.
    turn : int
        The current turn, represented as 1 or -1.
    in_board_mask : int
        A bitmask to determine valid positions within the board.
    winner : int or None
        The winner of the game (1, -1, or 0 for a tie), or None if the game is ongoing.
    
    Methods:
    --------
    initiate_board():
        Initializes the board setup for a new game.
    
    make_mask():
        Creates and returns a bitmask representing the valid positions on the board.
    
    get_moves():
        Determines all possible moves for the current player.

    play(position=72):
        Plays a move at the specified position or selects one randomly if the position is invalid.

    is_full():
        Checks if the board is full.

    get_winner():
        Determines the winner based on the current board state.

    set_state(state):
        Sets the board and turn to the provided state.

    get_state():
        Returns a copy of the current state of the game.

    reset():
        Resets the game to its initial state.

    user_move(surface, width, height):
        Handles user interactions for making a move.

    show(surface, width, height):
        Displays the board on a pygame surface

    show_with_possible_moves(surface, width, height):
        Displays the board on a pygame surface with the possible moves highlighted in green
    """

    def __init__(self):
        self.player_bitboards = [None, 0, 0]
        self.initiate_board()
        self.colors = ["#808080", '#000000', '#06402B', '#FFFFFF']
        self.turn = 1
        self.in_board_mask = self.make_mask()
        self.winner = None

    def get_moves(self):
        """
        Determines all possible moves for the current player, categorized by direction.

        Returns:
        --------
        tuple:
            - moves_by_direction1 (list): Moves for positive shift directions.
            - moves_by_direction2 (list): Moves for negative shift directions.
            - moves (int): A bitboard representing all possible moves.
        """
        moves_by_direction1 = []
        moves_by_direction2 = []

        player = self.player_bitboards[self.turn]
        ennemy = self.player_bitboards[-self.turn]
        directions = [1, 8, 9, 10]

        for i in directions:
            moves_in_direction = 0
            mask = ennemy & (player >> i)
            while mask :
                mask = (mask >> i) & (~player) & self.in_board_mask
                positions = (mask) & (~ennemy)
                mask &= ~positions
                moves_in_direction |= positions

            if moves_in_direction:
                moves_by_direction1.append((i, moves_in_direction))

        for i in directions:
            moves_in_direction = 0
            mask = ennemy & (player << i)
            while mask :
                mask = (mask << i) & (~player) & self.in_board_mask
                positions = (mask) & (~ennemy)
                mask &= ~positions
                moves_in_direction |= positions
            if moves_in_direction:
                moves_by_direction2.append((i, moves_in_direction))

        moves_by_direction = [i[1] for i in moves_by_direction1 + moves_by_direction2]
        moves = 0
        if moves_by_direction:
            moves = reduce(lambda x, y: x | y, moves_by_direction)

        return moves_by_direction1, moves_by_direction2, moves

    def play(self, position=72):
        """
        Executes a move at the given position or selects a valid position randomly if invalid.

        Parameters:
        -----------
        position : int, optional
            The bit position where the move is to be played (default is 72 which is always invalid).
        """
        moves_by_direction1, moves_by_direction2, moves = self.get_moves()

        if not ((1 << position) & moves):
            position = random.choice([i for i in range(moves.bit_length()) if (moves >> i) & 1])

        directions1 = [i[0] for i in moves_by_direction1 if ((1 << position) & i[1])]
        directions2 = [i[0] for i in moves_by_direction2 if ((1 << position) & i[1])]

        self.player_bitboards[self.turn] |= 1 << position

        player = self.player_bitboards[self.turn]

        for i in directions1:
            mask = 1 << position
            while mask != 0:
                mask = (mask << i) & (~player) & self.in_board_mask
                self.player_bitboards[self.turn] |= mask
                self.player_bitboards[-self.turn] &= ~mask

        for i in directions2:
            mask = 1 << position
            while mask != 0:
                mask = (mask >> i) & (~player) & self.in_board_mask
                self.player_bitboards[self.turn] |= mask
                self.player_bitboards[-self.turn] &= ~mask

        self.turn = -self.turn

        _, _, moves = self.get_moves()

        if moves == 0:
            self.turn = -self.turn
            _, _, moves = self.get_moves()
            if moves == 0:
                self.winner = self.get_winner()

    def is_full(self):
        """
        Checks if the board is full.

        Returns:
        --------
        int:
            A mask representing filled positions.
        """
        return self.player_bitboards[1] | self.player_bitboards[-1] == self.in_board_mask


    def get_winner(self):
        """
        Determines the winner based on the board state.

        Returns:
        --------
        int:
            1 if player 1 wins, -1 if player -1 wins, 0 for a tie.
        """
        score1 = bin(self.player_bitboards[1]).count('1')
        score_1 = bin(self.player_bitboards[-1]).count('1')
        difference = score1 - score_1
        return difference / abs(difference) if difference else 0

    def set_state(self, state):
        """
        Sets the game state to the provided state.

        Parameters:
        -----------
        state : tuple
            A tuple containing the player bitboards and turn.
        """
        temp_state = copy.deepcopy(state)
        self.player_bitboards = temp_state[0]
        self.turn = temp_state[1]

    def get_state(self):
        """
        Returns a copy of the current state of the game.

        Returns:
        --------
        tuple:
            A tuple containing the player bitboards and turn.
        """
        return copy.deepcopy([self.player_bitboards, self.turn])


    def reset(self):
        """
        Resets the game to its initial state.
        """
        self.player_bitboards = [None, 0, 0]
        self.initiate_board()
        self.turn = 1
        self.winner = None


    def show(self, surface, width, height):
        """
        Displays the current game state on a Pygame surface.

        Parameters:
        -----------
        surface : pygame.Surface
            The surface to draw the game board on.
        width : int
            The width of the game board.
        height : int
            The height of the game board.
        """
        pygame.draw.rect(surface, "#189AB4", pygame.Rect(0, 0, width, height))
        for i in range(8):
            for j in range(8):
                position = (7-i + j*9)
                player = int(((self.player_bitboards[1] >> position) & 1) - ((self.player_bitboards[-1] >> position) & 1))
                color = self.colors[player]
                pygame.draw.circle(surface, color, ((j+0.5)*width/8,(i+0.5)*height/8), 30)

    def show_with_possible_moves(self, surface, width, height):
        """
        Displays the current game state on a Pygame surface with the possible moves to play.

        Parameters:
        -----------
        surface : pygame.Surface
            The surface to draw the game board on.
        width : int
            The width of the game board.
        height : int
            The height of the game board.
        """
        _,_,moves = self.get_moves()

        pygame.draw.rect(surface, "#189AB4", pygame.Rect(0, 0, width, height))
        for i in range(8):
            for j in range(8):
                position = (7-i + j*9)
                player = int(((self.player_bitboards[1] >> position) & 1) - ((self.player_bitboards[-1] >> position) & 1)) + 2*((moves >> position) & 1)
                color = self.colors[player]
                pygame.draw.circle(surface, color, ((j+0.5)*width/8,(i+0.5)*height/8), 30)

    def user_move(self, surface, width, height):
        """
        Handles user interactions to play a move.

        Parameters:
        -----------
        surface : pygame.Surface
            The surface on which the game is drawn.
        width : int
            The width of the surface.
        height : int
            The height of the surface.
        """
        finished = False
        step = (width // 8)
        _, _, moves = self.get_moves()
        moves = [i for i in range(moves.bit_length()) if (moves >> i) & 1]

        while not finished:
            events = pygame.event.get()
            pos = pygame.mouse.get_pos()
            i = pos[0] // step
            j = pos[1] // step
            move = 9 * i + 7 - j
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP and (move in moves):
                    self.play(move)
                    return

            self.show_with_possible_moves(surface, width, height)
            if move in moves:
                pygame.draw.circle(surface, "#8B0000", ((i + 0.5) * width / 8, (j + 0.5) * height / 8), 30)

            pygame.display.flip()

    def initiate_board(self):
        """
        Initialize the board by setting specific positions on the bitboard.

        This function sets predefined positions on the player's bitboards to 
        represent the initial state of the game. It places two pieces for 
        each player in the center of the board.

        Modifies:
        ----------
        self.player_bitboards : list
            Updates the bitboards for both players to reflect the starting positions.
        """
        self.player_bitboards[1] |= 1 << 3*9+7-4
        self.player_bitboards[1] |= 1 << 4*9+7-3
        self.player_bitboards[-1] |= 1 << 3*9+7-3
        self.player_bitboards[-1] |= 1 << 4*9+7-4

    def make_mask(self):
        """
        Generate a bit mask covering all valid board positions.

        This function creates a bitmask representing all positions on the board 
        that can be occupied. The board is an 8x8 grid, and the mask 
        ensures that all positions are included.

        Returns:
        --------
        int
            A bitmask with all valid board positions set to 1.
        """
        mask = 0
        for i in range(8):
            for j in range(8):
                mask |= 1 << j*9 + 7-i
        return mask


def display_bits_in_grid(num):
    """
    display a 72-bit integer in a 9*8 grid.

    Parameters:
    -----------
    num : int
        integer to display
    """

    binary = bin(num)[2:].zfill(72)  
    binary = binary[-72:]

    grid = [[0 for _ in range(8)] for _ in range(9)]


    for bit_position in range(72):
        row = bit_position % 9
        col = 7 - bit_position // 9
        grid[row][col] = int(binary[bit_position])

    for row in (grid):
        print(" ".join(map(str, row)))