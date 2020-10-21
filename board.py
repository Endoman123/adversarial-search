import numpy as np

class Board():
    _board = np.array([])
   
    # Initialize the board with some multiple d
    # The board will be 3dx3d large.
    def __init__(self, d):
        size = 3d
        
        # Step 1: Initialize an empty board
        board = np.array([["_" for _ in range(size)] for _ in range(size)])
       
        # Step 2: Populate with pieces 
        board[0][::3] = ["W" for _ in range(d)] 
        board[0][1::3] = ["H" for _ in range(d)] 
        board[0][2::3] = ["M" for _ in range(d)]
        board[size - 1][::3] = ["w" for _ in range(d)] 
        board[size - 1][1::3] = ["h" for _ in range(d)] 
        board[size - 1][2::3] = ["m" for _ in range(d)]

        self._board = board

    def __repr__(self):
        pass

if __name__ = "__main__":
    board = Board(3)



