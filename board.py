import numpy as np
from collections import abc as cabc
import itertools

# Board representation
# Char board, with Originator structure
class Board(cabc.Sequence):
    # Initialize the board with some multiple d
    # The board will be 3dx3d large.
    def __init__(self, d):
        size = 3 * d
        
        # Step 1: Initialize an empty board
        board = np.array([["_" for _ in range(size)] for _ in range(size)])
        """
        Creating the probability arrays. I'm open to doing this another way but this was to get the probability into some sort of code
        p_w = np.array([[0 for _ in range(size)] for _ in range(size)])
        p_h = np.array([[0 for _ in range(size)] for _ in range(size)])
        p_m = np.array([[0 for _ in range(size)] for _ in range(size)])
        p_p = np.array([[0 for _ in range(size)] for _ in range(size)])
        """
       
        # Step 2: Populate with pieces 
        board[0][::3]= ["W" for _ in range(d)]
        board[0][1::3] = ["H" for _ in range(d)] 
        board[0][2::3] = ["M" for _ in range(d)]
        board[size - 1][::3] = ["w" for _ in range(d)] 
        board[size - 1][1::3] = ["h" for _ in range(d)] 
        board[size - 1][2::3] = ["m" for _ in range(d)]




        """
        Setting the correct in
            p_w[size - 1][::3].p_w = [1.0 for _ in range(d)]
            p_h[size - 1][1::3] = [1.0 for _ in range(d)] 
            p_m[size - 1][2::3] = [1.0 for _ in range(d)]
            for i in range(1, size - 1):
                for j in range(1, size):
                    p_p[i][j] = (d/3 - 1) / d
        """


        # Step 3: Populate with pits
        board[range(1, size - 1), np.random.randint(size, size = size - 2)] = ["O" for _ in range(size - 2)]

        """
        for i in range(1, d-1):
            for j in range(0, d-1):
                p_p[i][j] = (d/3 - 1)/d
        """

        # Step 4: Assign class members
        self._board = board
        self._size = size
        self._fow = False
    
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
    def restore(self, memento):
        board = []
        m_arr = memento.split("/")

        for row in m_arr:
            board_r = []
           
            num = ""
            for c in row:
                if c.isdigit():
                    num += c 
                else:
                    if num:
                        board_r += ["_" for _ in range(int(num))] 
                        num = ""

                    board_r += c 

            if num:
                board_r += ["_" for _ in range(int(num))]

            if len(board_r) != len(self):
                print(memento) 
                print(board_r) 
                raise Exception(f"Board sizes not equal! {len(board_r)} != {len(self)}")

            board += [board_r] 
        
        self._board = np.array(board)

    # Perform move
    # This assumes that whatever move you do is a valid move
    # Will throw an exception otherwise
    # Returns the score of the move:
    def move(self, a, b):
        p_from = self._board[a[0], a[1]]
        p_to = self._board[b[0], b[1]]
       
        if p_from != "_" and p_from != "O": # A valid piece to move
            if p_to == "_": # Empty location
                p_to = p_from

            elif p_to == "O": # Pit
                pass

            elif p_from.isupper() != p_to.isupper(): # Battle
                c_from = p_from.lower()
                c_to = p_to.lower()

                if (c_from == "h" and c_to == "w" or
                    c_from == "m" and c_to == "h" or
                    c_from == "w" and c_to == "m"): # Winning fight
                        p_to = p_from

                elif c_from == c_to: # Tie, both pieces are destroyed
                    p_to = "_"

            else: # Same pieces, invalid move
                raise Exception("Invalid move!")

        else: # Not a piece, invalid move
            raise Exception("Invalid move!")

        self._board[a[0], a[1]] = "_"
        self._board[b[0], b[1]] = p_to
            
    # Move generator
    # Returns a dict of moves based on whether you are major or minor
    # For the sake of this, major/minor refers to the case of the piece
    def generate_moves(self, major):
        moves = [] 
        b_size = self._size
        b = self._board

        for r in range(b_size):
            for c in range(b_size):
                p = b[r][c]
                p_set = "WHM" if major else "whm"

                if p in p_set:
                    c_from = (r, c)
                    p_moves = []
                    for i in (r - 1, r + 1):
                        if not 0 <= i < b_size:
                            continue
                        for j in range(max(0, c - 1), min(b_size, c + 2)):
                            p_to = b[i][j]
                            if p_to not in p_set: # Check if move is valid
                                moves += [(c_from, (i, j))] 
        
        return moves
   
    # Generates an 'observation'
    # Returns a string containing the relevant pieces surrounding it,
    # no repeats.
    def observe(self, x, y):
        if not 0 <= x < self._size or not 0 <= y < self.size:
            raise Exception("Cannot observe outside of board!")
    
        ret = ""
        board = self._board
        b_size = self._size
        piece = board[y, x]

        if piece in "WHMwhm": # We can do an observation here
            team = "WHM" if piece.isupper() else "whm" 

            for r in range(max(0, y - 1), min(b_size, y + 2)): 
                for c in range(max(0, x - 1), min(b_size, x + 2)):
                    if r == y and c == x:
                        continue
                    
                    cur_piece = board[r, c]
                    if cur_piece not in f"{team}_{ret}": # Test string checks if valid observation
                        ret += cur_piece

        return ret

    # Updates the probabilties for one of the units
    # c = # of total units remainging
    # prob = specific probability table being use
    def update_after_opp(self, c, prob):
        d = len(prob)
        new_prob = prob
        for i in range(d):
            for j in range(len(prob)):
                new_prob[i][j] = (1 - 1/c) * prob[i][j]
                sum = 0
                for x in range(max(0, i - 1), min(d, i + 2)):
                    for y in range(max(0, j - 1), min(d, j + 2)):
                        # Need way to easily get number of neighbors
                        sum += prob[x][y] * 1/(c * num)
                new_prob[i][j] += sum

    # Know that we will change how we do the probability tables. Just want  to get it out
    # Updates the probabilities before player moves, surveying where all current pieces are
    def update_on_player(self, occupied, p_p, p_w, p_h, p_m):

        # Fringe to hold all cells that contain observations
        fringe = []
        for (x,y) in occupied:
            observation = self.observe(x, y)
            if observation != "":
                fringe.append((x, y, observation))
            # If there is no observation, set prob for all adjacent cells to 0
            else:
                for i in range(max(0, x - 1), min(self._size, x + 2)):
                    for j in range(max(0, y - 1), min(self._size, y + 2)):
                        p_w[i][j] = 0
                        p_h[i][j] = 0
                        p_m[i][j] = 0
                        p_p[i][j] = 0
        # Will be used for caluclation P(O) and P(U|O)
        units = ""
        max_p = 0
        max_h = 0
        max_m = 0
        max_w = 0
        # Loop to find all the possible cells adjacent to our units that can contain an enemy unit
        # Also records the max number of possible units in those cells as well
        while len(fringe) != 0:
            (x,y, observation) = fringe.pop()
            current_adj = []
            for i in range(max(0, x - 1), min(self._size, x + 2)):
                for j in range(max(0, y - 1), min(self._size, y + 2)):
                    current_adj.append(i, j)
                    if observation == "b":
                        units+= "p"
                        max_p += 1
                    elif observation == "s":
                        units += "w"
                        max_w += 1
                    elif observation == "n":
                        units += "h"
                        max_h += 1
                    else:
                        units += "m"
                        max_m += 1
        max_pieces = len(units)
        # Gets the alpha value for each distribution for normalization
        alpha_m = self.get_alpha(p_m)
        alpha_p = self.get_alpha(p_p)
        alpha_h = self.get_alpha(p_h)
        alpha_w = self.get_alpha(p_w)

        # Gets all the possible combinations of units and cell locations
        data = [0] * max_pieces
        combos = []
        self.combo_location(current_adj, combos, data, 0, len(current_adj) - 1, 0, max_pieces)
        unit_combos = self.unit_combos(units)

        #Calculates the P(O) value
        p_o = self.get_p_o(unit_combos, combos, alpha_w, alpha_m, alpha_h, alpha_p, max_w, max_h, max_m, max_p, p_p, p_h, p_w, p_m)

        # Adjusts the probability for all possible cells with an enemy unit using P(O)
        for (x,y) in current_adj:
            p_p[x][y] *= p_o
            p_h[x][y] *= p_o
            p_m[x][y] *= p_o
            p_w[x][y] *= p_o

    # Finds the P(O) value using all the possible unit combos, cell combos, alpha values, and max unit values
    def get_p_o(self, unit_combos, location_combos, alpha_w, alpha_m, alpha_h, alpha_p,max_w, max_h, max_m, max_p, p_p, p_h, p_w, p_m):
        sum = 0
        for units in unit_combos:
            for cells in location_combos:
                cur_prob = 1
                cur_p = max_p
                cur_w = max_w
                cur_h = max_h
                cur_m = max_m
                for i in range(len(cells)):
                    (x, y) = cells[i]
                    if i >= len(units):
                        break
                    if units[i] == "p":
                        cur_prob *= alpha_p * p_p[x][y] * cur_p
                        cur_p -= 1
                    elif units[i] == "w":
                        cur_prob *= alpha_w * p_w[x][y] * cur_w
                        cur_w -= 1
                    elif units[i] == "m":
                        cur_prob *= alpha_m * p_m[x][y] * cur_m
                        cur_m -= 1
                    else:
                        cur_prob += alpha_h * p_h[x][y] * cur_h
                        cur_h -= 1
                sum += cur_prob
        return sum

    def unit_combos(self, units):
        result = []
        for i in range(len(units)):
            self.get_combos(units, 0, i, "", result)

        return result

    def get_unit_combos(self, units, start, depth, prefix, result):
        for i in range(start, len(units)):
            next = prefix + units[i]
            if (depth > 0):
                self.get_combos(units, i+1, depth - 1, next)
            else:
                result.append(next)

    def combo_location(self, arr, combos,data, start,
                        end, index, r):
        if (index == r):
            combos.append(data)
            return;
        i = start;
        while (i <= end and end - i + 1 >= r - index):
            data[index] = arr[i];
            self.combo_location(arr, combos, data, i + 1,
                                 end, index + 1, r);
            i += 1;

    #Gets the current alpha value for a specific probability
    def get_alpha(self, prob):
        sum = 0
        for i in range(self._size):
            for j in range(self._size):
                sum += prob[i][j]
        return 1/sum

    # Normalizes probability for specific distribution
    # r = # of remaining pieces for that specific unit
    def normalize_prob(self, prob, r):
        alpha = self.get_alpha(prob)
        for i in range(self._size):
            for j in range(self._size):
                prob[i][j] = prob[i][j] * r * alpha


    def toggle_fow(self):
        self._fow = not self._fow

    def get_fow(self):
        return self._fow

    def __getitem__(self, i):
        return self._board[i]

    def __len__(self):
        return self._size

    def __repr__(self):
        from os import linesep

        ret = "" 
        sep = "+" + ("---+" * (self._size))

        ret += sep + linesep
        
        for i in range(self._size):
            row = self._board[i] 

            ret += "| " + " | ".join(row) + " |"
            ret += linesep
            ret += sep

            if i < self._size - 1:
                ret += linesep

        return ret

