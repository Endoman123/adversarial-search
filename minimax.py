import numpy as np
from math import *
from queue import PriorityQueue
from board import Board
from heuristics import *

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
            moves_queue.put((-h(board = board, major = is_major), m))
            
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

# Minimax using fog of war probability calculations
# board: Board state
# prime: Board probabilities, map of 2d arrays
# depth: Current depth to search
# is_major: Whether the player is the major player
# h: Heuristic function, defaults to h_disable
# a: Alpha
# b: Beta
# Returns the move and value best suited to transition into the most optimal state
def minimax_p(board, prime, depth, is_major, h = h_disable, a = -inf, b = inf):
    pass

""""
def update()
    c = # of opponents pieces --> evaluate()
    board_prev = board from previous step
    For each cell in old_board
        cell.prob_wumpus = (1-1/c) * cell.prob_wumpus
        for each neighbor of cell (use x+1, x-1 or whatever to get the neighbors)
            sum += neighbor_cell.prob_wumpus * 1/(c * # of neighbors)
        cell.prob_wumpus += sum
    Repeat this process for each type of piece, pits are not updated
    
    For each cell containing our units
    If cell has no stench, then for each adjacent cell
        cell.prob_wumpus = 0
    If cell does receive stench,
        For each of the adjacent cells to the current one,
            Sum the probability of wumpus being in that cell
            Store this as sum
        Then for each adjacent cell
            Set cell.prob_wumpus = cell.prob_wumpus/sum
        For each non-adjacent cells
            cell.prob_wumpus = cell.prob_wumpus * (# of wumpi - 1/ # of wumpi)
Repeat for each types of unit
"""
"""
Algorithm Overview
1. First Initialize The Probabilities
When Placing Pieces, set the probability that that cell has a piece to 1.
Set the probability of it containing any other type of piece or pit to 0
For the rest of the board, set P(W), P(H), and P(M) to 0, and set P(P) to (d/3-1)/d where d is the length of the board
We have to update the board structure to have cells that contain the probability for each of the pieces and the pit
UI also needs to be updated to include probabilities on display during FOW display
2. First update probabilities after opponent moves
Set c = # of remaining opponent pieces
After the opponent moves, for each type of unit, update the probabilities of the unit being there
Might have to have two board structures, if updating probabilities on one board, will lead to incorrect calculations
For each cell in old_board
    cell.prob_wumpus = (1-1/c) * cell.prob_wumpus
    for each neighbor of cell (use x+1, x-1 or whatever to get the neighbors)
        sum += neighbor_cell.prob_wumpus * 1/(c * # of neighbors)
    cell.prob_wumpus += sum
Repeat this process for each type of piece, pits are not updated
3. Then run the observe function on each of for the cells of each of your pieces
For each cell containing our units
    If cell has no stench, then for each adjacent cell
        cell.prob_wumpus = 0
    If cell does receive stench,
        For each of the adjacent cells to the current one,
            Sum the probability of wumpus being in that cell
            Store this as sum
        Then for each adjacent cell
            Set cell.prob_wumpus = cell.prob_wumpus/sum
        For each non-adjacent cells
            cell.prob_wumpus = cell.prob_wumpus * (# of wumpi - 1/ # of wumpi)
Repeat for each types of unit
Might still have to have two copies of board, one old, one new. Not sure tho
4. After we move, for the piece that was moved, we run the observe function
Basically do step 3 but for just that cell for the piece that was moved.

1. Normalize the Probability
Do this after each of the four steps above
    Sum = None
    for each cell in board
        Sum+= cell.prob_wumpus
    alpha = 1/sum
    Let w be the number of Wumpi
    for each cell in board
        cell.prob_wumpus = alpha * cell.prob_wumpus * w
2. After performing the observe function for a cell
    If it has a stench
        Place all adjacent cells with non-zero probabilities into a list for the unit generating the observation
        Do this for each type of unit
        sum = Have to find probabilities for all configurations
            For each entry in each list
                sum += alpha_W*cell1.prob_wumpus*w * alpha_M*cell2.prob_mage*m
        For each entry in each list
            cell.prob_wumpus = cell.prob_wumpus * sum
        Do for all lists and types of units
"""
