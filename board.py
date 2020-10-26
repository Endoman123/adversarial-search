import numpy as np
from collections import abc as cabc

# Board representation
# Char board, with Originator structure
class Board(cabc.Sequence):
    # Initialize the board with some multiple d
    # The board will be 3dx3d large.
    def __init__(self, d):
        size = 3 * d
        
        # Step 1: Initialize an empty board
        board = np.array([["_" for _ in range(size)] for _ in range(size)])
       
        # Step 2: Populate with pieces 
        board[0][::3]= ["W" for _ in range(d)] 
        board[0][1::3] = ["H" for _ in range(d)] 
        board[0][2::3] = ["M" for _ in range(d)]
        board[size - 1][::3] = ["w" for _ in range(d)] 
        board[size - 1][1::3] = ["h" for _ in range(d)] 
        board[size - 1][2::3] = ["m" for _ in range(d)]

        # Step 3: Populate with pits
        board[range(1, size - 1), np.random.randint(size, size = size - 2)] = ["O" for _ in range(size - 2)]

        # Step 4: Assign class members
        self._board = board
        self._size = size
    
    # Create memento
    def create_memento(self):
        ret = [] 

        for row in self._board:
            str_r = "" 
            empty = 0
            for c in row:
                if c == "_":
                    empty += 1
                else:
                    if empty > 0:
                        str_r += str(empty)
                        empty = 0

                    str_r += c
            
            if empty > 0:
                str_r += str(empty)

            ret += [str_r]

        return "/".join(ret)

    # Restore state from memento
    def restore(self, memento):
        board = []
        m_arr = memento.split("/")

        for row in m_arr:
            board_r = []
            
            for c in row:
                if c.isdigit():
                    board_r += ["_" for _ in range(int(c))]
                else:
                    board_r += c
                
            if len(board_r) != len(self):
                raise Exception(f"Board sizes not equal! {len(board_r)} != {len(self)}")

            board += [board_r] 
        
        self._board = np.array(board)

    # Perform move
    # This assumes that whatever move you do is a valid move
    # Will throw an exception otherwise
    # Returns the score of the move:
    def move(self, a, b):
        p_from = self._board[a[0], a[1]]
        p_to = self._board[b[0], b[1]]
       
        if p_from != "_" and p_from != "O": # A valid piece to move
            if p_to == "_": # Empty location
                p_to = p_from

            elif p_to == "O": # Pit
                pass

            elif p_from.isupper() != p_to.isupper(): # Battle
                c_from = p_from.lower()
                c_to = p_to.lower()

                if (c_from == "h" and c_to == "w" or
                    c_from == "m" and c_to == "h" or
                    c_from == "w" and c_to == "m"): # Winning fight
                        p_to = p_from

                elif c_from == c_to: # Tie, both pieces are destroyed
                    p_to = "_"

            else: # Same pieces, invalid move
                raise Exception("Invalid move!")

        else: # Not a piece, invalid move
            raise Exception("Invalid move!")

        self._board[a[0], a[1]] = "_"
        self._board[b[0], b[1]] = p_to
            
    # Move generator
    # Returns a dict of moves based on whether you are major or minor
    # For the sake of this, major/minor refers to the case of the piece
    def generate_moves(self, major):
        moves = [] 
        b_size = self._size
        b = self._board

        for r in range(b_size):
            for c in range(b_size):
                p = b[r][c]
                is_piece = p.lower() in "whm"
                is_side = p.isupper() == major

                if is_piece and is_side:
                    c_from = (r, c)
                    p_moves = []
                    for i in (r - 1, r + 1):
                        if not 0 <= i < b_size:
                            continue
                        for j in range(max(0, c - 1), min(b_size, c + 2)):
                            p_to = b[i][j]
                            if not p_to.lower() in "whm" or p.isupper() != major: # Check if move is valid
                                moves += [(c_from, (i, j))] 

        return moves

    def __getitem__(self, i):
        return self._board[i[0]]

    def __len__(self):
        return self._size

    def __repr__(self):
        from os import linesep

        ret = "" 
        sep = "+" + ("---+" * (self._size))

        ret += sep + linesep
        for row in self._board:
            ret += "| " + " | ".join(row) + " |"
            ret += linesep
            ret += sep + linesep 

        return ret

