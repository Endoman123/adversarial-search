import numpy as np
from board import Board
from minimax import *

# Abstract class that defines a player
# No idea how to do pythonic interfaces,
# so no function enforcing here.
class Player():
    def __init__(self, board, major):
        self._board = board
        self._major = major

# Player that makes moves based on command-line input
class CLIPlayer(Player):
    def get_move(self):
        moves = self._board.generate_moves(self._major)
       
        while True:
            print(moves) 
            p_fromstr = input("Choose piece (as \"r c\"): ").strip()
            p_from = tuple([int(i) for i in p_fromstr.split()])
                
            moves_sub = [m for m in moves if m[0] == p_from]
            if moves_sub:
                moves = moves_sub 
                break

        while True:
            print(moves)
            p_tostr = input("Choose destination (as \"r c\"): ").strip()
            p_to = tuple([int(i) for i in p_tostr.split()])

            if any(m[1] == p_to for m in moves):
                break

        return p_from, p_to

# Player that makes moves based on minimax algorithm
class AIPlayer(Player):
    def __init__(self, board, major, depth):
        super().__init__(board, major)

        self._depth = depth

    def get_move(self):
        ret = minimax(self._board, self._depth, self._major)
        print(ret)
        return ret[1] 
