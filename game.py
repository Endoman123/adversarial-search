import os
from player import *
from board import Board

board = None
p1 = None
p2 = None

if __name__ == "__main__":
    board = Board(3)
    p1 = CLIPlayer(board, True)
    p2 = AIPlayer(board, False, 4)

    running = True
    move = None  

    while running:
        print(board)

        if len(board.generate_moves(True)) > 0:
            move = p1.get_move()
            board.move(move[0], move[1])
        else:
            running = False
            break

        if len(board.generate_moves(False)) > 0:
            move = p2.get_move()
            board.move(move[0], move[1])
        else:
            running = False
            break

        print()
