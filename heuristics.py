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
    ret = -inf 

    moves = tuple(m[1] for m in board.generate_moves(kwargs["major"]))

    return sum(1 for m in moves if board[m[0]][m[1]] != "O")

# Gets manhattan difference between Wumpus/Mage, Hero/Wumpus, and Mage/Hero
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
 
# Gets Euclidean difference between Wumpus/Mage, Hero/Wumpus, and Mage/Hero
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

# Tries to maximize space between pieces
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
