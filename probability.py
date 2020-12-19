import board
import numpy as np
import itertools

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
def eval():
   pass 


# Updates all of the probability boards after the opponent has moved
# remaining = total remaining pieces
# prob_table = dictionary of the probability tables
def update_probabilities(remaining, prob_table):
    transition(prob_table['W'], remaining["W"])
    transition(prob_table['H'], remaining["H"])
    transition(prob_table['M'], remaining["M"])
    # prob_table['O'] = normalize_prob(prob_table['O'], remaining['O'])

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


def guess_move(board, major, prob_table, remaining):
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
        temp = eval(move)

        if temp > best:
            ret = move
            best = temp

    return ret 


# Function to update an probability table
# c = # of remaining pieces for that specific unit
# prob = the probability table
# neighbors = a 2d table which counts the number of viable neighbors each cell on the board has
def update_after_opp(c, prob, neighbors):
    d = len(prob)
    new_prob = prob

    # Assumes that the opponent has an equal chance of moving any pieces to any adjacent spot
    for i in range(d):
        for j in range(len(prob)):
            new_prob[i][j] = (1 - 1 / c) * prob[i][j]
            sum = 0
            for x in range(max(0, i - 1), min(d, i + 2)):
                for y in range(max(0, j - 1), min(d, j + 2)):
                    # Adds to sum
                    sum += prob[x][y] * 1 / (c * neighbors[x][y])
            new_prob[i][j] += sum

    # Normalize the probability to ensure Bayes rule is satisfied
    prob = normalize_prob(new_prob, c)
    return prob


# Function that updates the probability tables after the player has moved
# Occupied = a list of all the cells currently occupied by the player's units
# prob_table = dictionary of all the probability tables
# Size = length of the board
def update_after_player(occupied, prob_table, size):
    # units is a string of all of the observations
    # max_units is a dictionary of the max number of pieces that can be adjacent to one of our units
    # adjacent is a list that will contain all the adjacent cells to an occupied cell that yields an observation
    units = ""
    max_units = {"O": 0, "W": 0, "H": 0, "M": 0}
    adjacent = []
    # First finds all of the occupied cells that yield observations
    for (x, y) in occupied:
        # Observe should return one of the following: "b", "s", "n", "h", or ""
        observation = board.Board.observe(x, y)

        # If there is a relevant observation, add all of its adjacent cells to the adjacent list
        if observation != "":
            for i in range(max(0, x - 1), min(size, x + 2)):
                for j in range(max(0, y - 1), min(size, y + 2)):
                    adjacent.append(i, j)

            # Increment the max number of units
            max_units[observation] += 1
            # Otherwise set all of the probabilities of the adjacent cells to 0
        else:
            for i in range(max(0, x - 1), min(size, x + 2)):
                for j in range(max(0, y - 1), min(size, y + 2)):
                    prob_table['W'][i][j] = 0
                    prob_table['M'][i][j] = 0
                    prob_table['H'][i][j] = 0
                    prob_table['O'][i][j] = 0

    # These functions find all the possible combinations of cells and units that could result from our observations
    data = [0] * len(units)
    combos = []
    combo_locations(adjacent, combos, data, 0, len(adjacent) - 1, 0, len(units))
    unit_combos = get_unit_combos(units)

    # Find the alpha values
    alphas = {"O": get_alpha(prob_table["O"]), "W": get_alpha(prob_table["W"]), "M": get_alpha(prob_table["M"]),
              "H": get_alpha(prob_table["H"])}

    # Calculates the P(O) value, then resets the probabilities on the board accordingly
    p_o = get_p_o(prob_table, unit_combos, combos, alphas, max_units)
    for (x, y) in adjacent:
        prob_table["W"][x][y] *= p_o
        prob_table["M"][x][y] *= p_o
        prob_table["H"][x][y] *= p_o
        prob_table["O"][x][y] *= p_o

