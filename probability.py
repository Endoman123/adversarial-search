import board
import numpy as np
import itertools
from math import *
from heuristics import *

# Initializes the probabilities boards in a map of 2d arrays
def initialize(size):
    d = int(size / 3)

    p_w = np.array([[0. for _ in range(size)] for _ in range(size)])
    p_h = np.array([[0. for _ in range(size)] for _ in range(size)])
    p_m = np.array([[0. for _ in range(size)] for _ in range(size)])
    p_o = np.array([[0. for _ in range(size)] for _ in range(size)])

    p_w[0][::3] = [1. for _ in range(d)]
    p_h[0][1::3] = [1. for _ in range(d)]
    p_m[0][2::3] = [1. for _ in range(d)]

    pit_prob = (1. - d / 3.) / d
    p_o[1:-1, :] = [ [ pit_prob for _ in range(size) ] for _ in range(1, size - 1) ] 

    prob_table = {"O": p_o, "W": p_w, "H": p_h, "M": p_m}
    remaining = {"W": d, "H": d, "M": d}

    return prob_table, remaining

def get_obs(board, prob_table, major):
    length = len(board)
    
    for y in range(length):
        for x in range(length):
            obs = board.observe(x, y, major)
            if not obs:
                for u in obs:
                    observation_update(prob_table[u], x, y, remaining)


# Probabilistics AI
def eval(move, prob_table):
    (y, x) = move[1]
    return sum(prob_table[u][y][x] for u in "WHM")


# Updates all of the probability boards after the opponent has moved
# remaining = total remaining pieces
# prob_table = dictionary of the probability tables
def update_probabilities(remaining, prob_table):
    transition(prob_table['W'], remaining["W"])
    transition(prob_table['H'], remaining["H"])
    transition(prob_table['M'], remaining["M"])


def transition(prob_board, c):
    prime_board = np.array(prob_board) 
  
    size = len(prime_board)
    for i in range(size):
        for j in range(size):
            # Neighbors calc
            neighbors = 0
            for m in (i - 1, i + 1):
                if not 0 <= m < size:
                    continue
                for n in range(max(0, j - 1), min(size, j + 2)):
                    neighbors += prime_board[m][n]  

            prob_board[i, j] = (1 - 1/c) * prime_board[i][j] + neighbors


# Normalize probabilities
def normalize(board):
    alpha = 1 / np.sum(board)
    np.copyto(board, np.multiply(alpha, board))


def observation_update(prob_board, x, y, remaining): 
    length = len(prob_board) 
    alpha = 1 / np.sum(prob_board[y - 1:y + 2, x - 1:x + 2])

    np.copyto(prob_board[y - 1:y + 2][x - 1: x + 2], np.multiply(alpha, prob_board[y - 1:y + 2][x - 1: x + 2]))

    for i in range(length):
        for j in range(length):
            if x + 1 >= i >= x - 1 and y + 1 >= j >= y - 1:
                continue

            prob_board[i][j] *= (remaining[observation] - 1) / remaining[observation]


def guess_move(board, major, prob_table, remaining, h = h_disable, w = 1):
    ret = None 
    best = -inf

    # Step 1: Generate moves
    moves = board.generate_moves(major)
    
    # Step 2: Update probabilities
    update_probabilities(remaining, prob_table) 
    get_obs(board, prob_table, major)
    
    # Normalize boards
    for a in "WHMO":
        normalize(prob_table[a])
   
    print(prob_table)

    # Step 3: Rate a best move based on the given
    for move in moves:
        temp = eval(move, prob_table) + h() * w

        if temp > best:
            ret = move
            best = temp

    return ret
