import board
import numpy as np
import itertools


# Initializes the probabilities boards in a map of 2d arrays
def initialize(d):
    size = d * 3

    p_w = np.array([[0 for _ in range(size)] for _ in range(size)])
    p_h = np.array([[0 for _ in range(size)] for _ in range(size)])
    p_m = np.array([[0 for _ in range(size)] for _ in range(size)])
    p_p = np.array([[0 for _ in range(size)] for _ in range(size)])

    p_w[size - 1][::3].p_w = [1.0 for _ in range(d)]
    p_h[size - 1][1::3] = [1.0 for _ in range(d)]
    p_m[size - 1][2::3] = [1.0 for _ in range(d)]
    for i in range(1, size - 1):
        for j in range(1, size):
            p_p[i][j] = (d / 3 - 1) / d

    prob_table = {"b": p_p, "s": p_w, "h": p_m, "n": p_h}
    return prob_table


# Probabilistics AI
def eval():
    pass


# Updates all of the probability boards after the opponent has moved
# remaining = dictionary of total remaining pieces
# prob_table = dictionary of the probability tables
# neighbors = 2D array of the number of neighbors each cell has
def transition(remaining, prob_table, neighbors):
    prob_table['s'] = update_after_opp(remaining['s'], prob_table['s'], neighbors)
    prob_table['h'] = update_after_opp(remaining['h'], prob_table['h'], neighbors)
    prob_table['n'] = update_after_opp(remaining['n'], prob_table['n'], neighbors)
    prob_table['b'] = normalize_prob(prob_table['b'], remaining['b'])


def guess_move():
    pass


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
    max_units = {"b": 0, "s": 0, "n": 0, "h": 0}
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
            # Append the observation itself to units
            if observation == "b":
                units += "p"
            elif observation == "s":
                units += "w"
            elif observation == "n":
                units += "h"
            else:
                units += "m"
            # Increment the max number of units
            max_units[observation] += 1
            # Otherwise set all of the probabilities of the adjacent cells to 0
        else:
            for i in range(max(0, x - 1), min(size, x + 2)):
                for j in range(max(0, y - 1), min(size, y + 2)):
                    prob_table['b'][i][j] = 0
                    prob_table['s'][i][j] = 0
                    prob_table['n'][i][j] = 0
                    prob_table['h'][i][j] = 0

    # These functions find all the possible combinations of cells and units that could result from our observations
    data = [0] * len(units)
    combos = []
    combo_locations(adjacent, combos, data, 0, len(adjacent) - 1, 0, len(units))
    unit_combos = get_unit_combos(units)

    # Find the alpha values
    alphas = {"b": get_alpha(prob_table["b"]), "s": get_alpha(prob_table["s"]), "h": get_alpha(prob_table["h"]),
              "n": get_alpha(prob_table["n"])}

    # Calculates the P(O) value, then resets the probabilities on the board accordingly
    p_o = get_p_o(prob_table, unit_combos, combos, alphas, max_units)
    for (x, y) in adjacent:
        prob_table["b"][x][y] *= p_o
        prob_table["s"][x][y] *= p_o
        prob_table["h"][x][y] *= p_o
        prob_table["n"][x][y] *= p_o


# Finds the P(O) value for a set of observations
# prob_table = dictionary of the probability tables
# unit_combos = all possible combinations of units
# location_combos = all possible location combinations
# alphas = dictionary of the alpha values
# max_units = dictionary of the max number of units for each unit type
def get_p_o(prob_table, unit_combos, location_combos, alphas, max_units):
    total = 0
    for units in unit_combos:
        for cells in location_combos:
            cur_prob = 1
            cur_p = max_units["b"]
            cur_w = max_units["s"]
            cur_h = max_units["n"]
            cur_m = max_units["h"]
            for i in range(len(cells)):
                (x, y) = cells[i]
                if i >= len(units):
                    break
                if units[i] == "p":
                    cur_prob *= alphas["b"] * prob_table["b"][x][y] * cur_p
                    cur_p -= 1
                elif units[i] == "w":
                    cur_prob *= alphas["s"] * prob_table["s"][x][y] * cur_w
                    cur_w -= 1
                elif units[i] == "m":
                    cur_prob *= alphas["h"] * prob_table["h"][x][y] * cur_m
                    cur_m -= 1
                else:
                    cur_prob += alphas["n"] * prob_table["n"][x][y] * cur_h
                    cur_h -= 1
            total += cur_prob
    return total

# Gets all of the location combinations
# arr = adjacent cells
# combos = originally empty list of combos
# data = array that will be used to fill the locations, then append to combos
# start = starting index
# end = end index
# index= current index
# r = max number of units possible
def combo_locations(arr, combos, data, start,
                    end, index, r):
    if index == r:
        combos.append(data)
        return
    i = start
    while i <= end and end - i + 1 >= r - index:
        data[index] = arr[i];
        combo_locations(arr, combos, data, i + 1,
                        end, index + 1, r)
        i += 1

# Gets all the possible combinations of units given our observations
# units = string of the different units from the observations
def get_unit_combos(units):
    result = []
    for i in range(len(units)):
        unit_combos(units, 0, i, "", result)
    return result


def unit_combos(units, start, depth, prefix, result):
    for i in range(start, len(units)):
        next = prefix + units[i]
        if (depth > 0):
            unit_combos(units, i + 1, depth - 1, next, result)
        else:
            result.append(next)

# Gets the alpha value for a probability table
def get_alpha(table):
    sum = 0
    for i in range(len(table)):
        for j in range(len(table[i])):
            sum += table[i][j]
    return 1 / sum

# Normalizes the probability for a table
def normalize_prob(table, r):
    alpha = get_alpha(table)
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = table[i][j] * r * alpha
    return table
