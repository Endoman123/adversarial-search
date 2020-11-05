import numpy as np
import pygame as pg
from pygame import *
from pygame.locals import *
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
            p_fromstr = input("Choose piece (as \"r c\"): ").strip()
            p_from = tuple([int(i) for i in p_fromstr.split()])
                
            moves_sub = [m for m in moves if m[0] == p_from]
            if moves_sub:
                moves = moves_sub 
                break

        while True:
            p_tostr = input("Choose destination (as \"r c\"): ").strip()
            p_to = tuple([int(i) for i in p_tostr.split()])

            if any(m[1] == p_to for m in moves):
                break

        return p_from, p_to

# Player that makes moves based on GUI inputs
class GUIPlayer(Player):
    c_from = None
    c_to = None

    c_moves = None

    def __init__(self, board, major, vis_pos, vis_csize, vis_margin, vis_gutter):
        super().__init__(board, major)

        self._board_pos = vis_pos
        self._cell_size = vis_csize
        self._margin = vis_margin
        self._gutter = vis_gutter

    # Update func for game loop
    # Only active when it is the turn
    def update(self, ev):
        # Init moveset 
        if not self.c_moves:
            self.c_moves = self._board.generate_moves(self._major)

        # Listen to mouse inputs 
        if ev.type == MOUSEBUTTONUP and ev.button == 1:
            # Store the moveset in a easy to use variable
            moves = self.c_moves

            # Convert mouse click to board pos 
            pos = tuple((a - b - self._margin) // (self._cell_size + self._gutter) for a, b in zip(ev.pos, self._board_pos))[::-1]
            
            if any(m[0] == pos for m in moves):
                self.c_from = pos
            elif self.c_from and any(m[1] == pos for m in moves if m[0] == self.c_from):
                self.c_to = pos
    
    def get_move(self):
        ret = None 

        if self.c_from and self.c_to:
            ret = (self.c_from, self.c_to)
            self.c_moves = None
            self.c_from = None
            self.c_to = None
       
        return ret

# Player that makes moves based on minimax algorithm
class AIPlayer(Player):
    def __init__(self, board, major, depth, h = h_disable):
        super().__init__(board, major)

        self._depth = depth
        self._heuristic = h

    def get_move(self):
        return minimax(self._board, self._depth, self._major, self._heuristic)[1] 
