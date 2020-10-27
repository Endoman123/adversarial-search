import numpy as np
from math import *
from queue import PriorityQueue
from board import Board

# Metric evaluation
# Simply use the difference between the number of pieces
# each side has
def evaluate(board):
    ret = 0

    # We use this as an easy way to count remaining pieces
    mm_eval = board.create_memento()

    n_major = sum(map(lambda x: x in "WHM", mm_eval))
    n_minor = sum(map(lambda x: x in "whm", mm_eval))

    # We need to cover winning states
    if n_major == 0: # Minor wins
        ret = -inf
    elif n_minor == 0: # Major wins
        ret = inf
    else: # Undecided
        ret = n_major - n_minor

    return ret

##
# Heuristic functions
# NOTE: Heuristic functions are meant to be agnostic
#       of the side that they are evaluated for,
#       i.e.: sign(major) == sign(minor)

# Dummy function to disable heuristic sorting
def h_disable(**kwargs):
    return 0

# Minimax with alpha-beta pruning
# board: Board state
# depth: Current depth to search
# is_major: Whether the player is the major player
# h: Heuristic function, defaults to h_disable
# a: Alpha
# b: Beta
# Returns the move and value best suited to transition into the most optimal state
def minimax(board, depth, is_major, h = h_disable, a = -inf, b = inf):
    b_metric = evaluate(board)
    b_moves = board.generate_moves(is_major) 
    ret = (b_metric, None)

    if depth == 0 or abs(b_metric) == inf:
        pass
    else:
        moves_queue = PriorityQueue() 
        sign = 1 if is_major else -1
        mm = board.create_memento()   
        opt_value = -inf * sign
        opt_move = ()

        for m in b_moves:
            moves_queue.put((sign * h(move = m), m))
            
        while not moves_queue.empty():
            item = moves_queue.get()
            move = item[1]
           
            # Perform move, evaluate
            board.move(move[0], move[1])
            c_minimax = minimax(board, depth - 1, not is_major, h, a, b)
            diff = c_minimax[0] - opt_value

            if diff * sign > 0:
                opt_value = c_minimax[0]
                opt_move = move

            board.restore(mm)

            if is_major:
                a = max(a, opt_value)
                if a >= b:
                    print("Beta cut-off") 
                    break
            else:
                b = min(b, opt_value)
                if b <= a:
                    print("Alpha cut-off") 
                    break

        ret = (opt_value, opt_move)

    return ret
