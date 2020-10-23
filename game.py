from player import *
from board import Board

if __name__ == "__main__":
    board = Board(3)
    p1 = CLIPlayer(board, True)
    p2 = CLIPlayer(board, False)

    while True:
        print(board) 
        c_move = p1.get_move()

        board.move(c_move[0], c_move[1])

