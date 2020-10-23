import numpy as np
from board import Board

class Player():
    def __init__(self, board, major):
        self._board = board
        self._major = major

class CLIPlayer(Player):
    def get_move(self):
        moves = self._board.generate_moves(self._major)
        
        p_fromstr = input("Choose piece (as \"r c\"): ").strip()
        p_from = tuple([int(i) for i in p_fromstr.split()])

        if moves[p_fromstr]:
            while True:
                p_tostr = input("Choose destination (as \"r c\"): ").strip()
                p_to = tuple([int(i) for i in p_tostr.split()])
                
                print(p_to)

                if p_to in moves[p_fromstr]:
                    break

        return p_from, p_to
