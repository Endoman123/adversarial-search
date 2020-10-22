import numpy as np

# Board representation
# Char board, with Originator structure
class Board():
    _board = np.array([])
   
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

        # Step 4: Assign class member
        self._board = board
    
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
    # Assume that the board size is the same
    def restore(self, memento):
        board = np.array([])
        m_arr = memento.split("/")

        for row in m_arr:
            board_r = []
            
            for c in row:
                if c.isdigit():
                    board_r += ["_" for _ in range(int(c))]
                else:
                    board_r += c

    def __repr__(self):
        return repr(self._board)

if __name__ == "__main__":
    board = Board(3)
    m = board.create_memento()
    board.restore(m)
    print(board)
