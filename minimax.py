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

# Advantage: Takes number of possible winning "fights"
def h_advantage(**kwargs):
    board = kwargs["board"]
    a_pieces = "WHM" if kwargs["major"] else "whm"
    b_pieces = "mwh" if kwargs["major"] else "MWH"
    ret = -inf

    mm = board.create_memento()
    
    a_team = (sum(1 for i in mm if i == p) for p in a_pieces)
    b_team = (sum(1 for i in mm if i == p) for p in b_pieces)

    if all(i > 0 for i in a_team):
        ret = sum(a - b for a, b in zip(a_team, b_team))

    return ret

# Moves: Takes number of viable moves
def h_moves(**kwargs):
    board = kwargs["board"]
    
    moves = tuple(m[1] for m in board.generate_moves(kwargs["major"]))

    return sum(1 for m in moves if board[m[0]][m[1]] != "O")
#Gets manhattan difference between Wumpus/Mage, Hero/Wumpus, and Mage/Hero
def h_manhattan(**kwargs):
    
    ret = 0
    board = kwargs["board"]
    
    a_set = "WHM" if kwargs["major"] else "whm"
    b_set = "mwh" if kwargs["major"] else "MWH"
    
    a_pos = tuple(tuple((x, y) for x in range(len(board)) for p in a_set for y in range(len(board)) if board[y][x] == p))
    b_pos = tuple(tuple((x, y) for x in range(len(board)) for p in b_set for y in range(len(board)) if board[y][x] == p))
    
    comp_pos = zip(a_pos, b_pos)
    # So at this point it should be (W * m, H * w, M * h)
   
    for comp in comp_pos:
        min_dist = inf
        a = comp[0]
        b = comp[1]
        #for a in comp[0]:
            #for b in comp[1]:
        min_dist = min(min_dist, sum(abs(m - n) for m, n in zip(a, b)))
                #print(min_dist)

        ret += min_dist
    
    # Should have the sum of the minimum distances
    return ret
 
#Gets Euclidean difference between Wumpus/Mage, Hero/Wumpus, and Mage/Hero
def h_euclidean(**kwargs):
    
    ret = 0
    board = kwargs["board"]
    
    a_set = "WHM" if kwargs["major"] else "whm"
    b_set = "mwh" if kwargs["major"] else "MWH"
    
    a_pos = tuple(tuple((x, y) for x in range(len(board)) for p in a_set for y in range(len(board)) if board[y][x] == p))
    b_pos = tuple(tuple((x, y) for x in range(len(board)) for p in b_set for y in range(len(board)) if board[y][x] == p))
    
    comp_pos = zip(a_pos, b_pos)
    # So at this point it should be (W * m, H * w, M * h)
   
    for comp in comp_pos:
        min_dist = inf
        a = comp[0]
        b = comp[1]
        #for a in comp[0]:
            #for b in comp[1]:
        min_dist = min(min_dist, sum((m - n) ** 2 for m, n in zip(a, b)) ** .5)

        ret += min_dist
    
    # Should have the sum of the minimum distances
    return ret
#Tries to maximize space between pieces
def h_spacing (**kwargs):
    board = kwargs["board"]
    ret = 0
    
    if (kwargs["major"]):
        a_set = "WHM" 
        pos_list = tuple(tuple((x, y) for x in range(len(board)) for p in a_set for y in range(len(board)) if board[y][x] == p))
        
        for pos in pos_list:
            max_dist = -inf
            for pos1 in pos_list:
                if (pos != pos1):
                    max_dist = max(max_dist, sum((m - n) for m, n in zip(pos, pos1)))
            ret += max_dist
    else:
        a_set = "whm" 
        pos_list = tuple(tuple((x, y) for x in range(len(board)) for p in a_set for y in range(len(board)) if board[y][x] == p))
        
        for pos in pos_list:
            max_dist = -inf
            for pos1 in pos_list:
                if (pos != pos1):
                    max_dist = max(max_dist, sum((m - n) for m, n in zip(pos, pos1)))
            ret += max_dist
    
    return ret
    
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
   # print (b_moves)
    if depth == 0 or abs(b_metric) == inf:
        pass
    else:
        moves_queue = PriorityQueue() 
        sign = 1 if is_major else -1
        mm = board.create_memento()   
        opt_value = -inf * sign
        opt_move = ()

        for m in b_moves:
            #print ("hello")
            moves_queue.put((sign * h(board = board, major = is_major), m))
            
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
                    break
            else:
                b = min(b, opt_value)
                if b <= a:
                    break

        ret = (opt_value, opt_move)

    return ret
