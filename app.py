from player import *
from board import Board
import pygame
from pygame import *
from pygame.locals import *

vis_board = None
vis_overlay = None
vis_pieces = None
vis_pos = (10, 10)
vis_margins = 10
vis_gutters = 5
vis_csize = 50

sprites = {
    "W": None,
    "H": None,
    "M": None,
    "w": None,
    "h": None,
    "m": None,
}

board = None
p1 = None
p2 = None
cur_turn = True

running = False

def init():
    global vis_board, vis_overlay, vis_csize, vis_margins, vis_pieces, vis_gutters, sprites, board, p1, p2
    
    board = Board(3)
    p1 = GUIPlayer(board, True, vis_pos, vis_csize, vis_margins, vis_gutters)  
    p2 = AIPlayer(board, False, 4)

    board_size = len(board)

    vis_bwidth = vis_margins + vis_gutters * board_size - vis_gutters + vis_csize * board_size
    vis_owidth = vis_bwidth - vis_margins 

    vis_board = Surface((vis_bwidth, vis_bwidth))
    vis_board.fill((0, 0, 0))

    vis_overlay = Surface((vis_owidth, vis_owidth), pygame.SRCALPHA)
    vis_pieces = Surface((vis_owidth, vis_owidth), pygame.SRCALPHA)

    for x in range(board_size):
        for y in range(board_size):
            color = (255, 255, 255) if board[y][x] != "O" else (100, 0, 0)
                
            x_pos = vis_margins + x * vis_csize + x * vis_gutters - x
            y_pos = vis_margins + y * vis_csize + y * vis_gutters - y
           
            pygame.draw.rect(vis_board, color, (x_pos, y_pos, vis_csize, vis_csize))

    c_major = Surface((vis_csize, vis_csize))
    c_major.fill((0, 0, 255))

    c_minor = Surface((vis_csize, vis_csize))
    c_minor.fill((255, 0, 0)) 

    spr_wumpus = pygame.image.load("wumpus.png")
    spr_wumpus = pygame.transform.scale(spr_wumpus, (vis_csize, vis_csize))
    
    spr_humanoid = pygame.image.load("humanoid.png")
    spr_humanoid = pygame.transform.scale(spr_humanoid, (vis_csize, vis_csize))

    spr_bow = pygame.image.load("bow.png")
    spr_bow = pygame.transform.scale(spr_bow, (vis_csize, vis_csize))

    spr_wand = pygame.image.load("wand.png")
    spr_wand = pygame.transform.scale(spr_wand, (vis_csize, vis_csize))

    sprites.update({a: spr_wumpus.copy() for a in "Ww"})
    sprites.update({a: spr_humanoid.copy() for a in "HhMm"})

    for a in "WHM":
        sprites[a].blit(c_major, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)
    
    for a in "whm":
        sprites[a].blit(c_minor, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)

    for a in "Hh":
        sprites[a].blit(spr_bow, (0, 0))

    for a in "Mm":
        sprites[a].blit(spr_wand, (0, 0))

def update(ev):
    global board, cur_turn, running, vis_csize, vis_gutters, vis_margins, p1, p2

    if cur_turn:
        p1.update(ev)

        move = p1.get_move()

        if move:
            board.move(move[0], move[1])
            cur_turn = False 
    else:
        move = p2.get_move()

        board.move(move[0], move[1])
        cur_turn = True
        print("Your turn")

def draw(screen): 
    global vis_pos, vis_board, vis_csize, vis_margins, vis_gutters, vis_pieces, sprites, board, p1

    vis_overlay.convert_alpha()
    vis_overlay.fill(0) 

    vis_pieces.convert_alpha()
    vis_pieces.fill(0) 

    if p1.c_from:
        x = p1.c_from[1]
        y = p1.c_from[0]

        x_pos = x * vis_csize + x * vis_gutters - x
        y_pos = y * vis_csize + y * vis_gutters - y
        
        pygame.draw.rect(vis_overlay, (20, 60, 40), (x_pos, y_pos, vis_csize, vis_csize))
        
        for to in tuple(a[1] for a in p1.c_moves if a[0] == p1.c_from):  
            x = to[1]
            y = to[0]
            
            color = (20, 40, 60)
            p_to = board[y][x]

            if p_to == "O":
                color = (60, 40, 60)
            elif p_to in "whm":
                color = (0, 100, 100)

            x_pos = x * vis_csize + x * vis_gutters - x
            y_pos = y * vis_csize + y * vis_gutters - y
            
            pygame.draw.rect(vis_overlay, color, (x_pos, y_pos, vis_csize, vis_csize))    

    for x in range(len(board)):
        for y in range(len(board)):
            p = board[y][x] 
            x_pos = x * vis_csize + x * vis_gutters - x
            y_pos = y * vis_csize + y * vis_gutters - y
            
            if p not in "_O" and sprites[p]:
                vis_pieces.blit(sprites[p], (x_pos, y_pos))

    screen.blit(vis_board, vis_pos) 
    screen.blit(vis_overlay, (vis_pos[0] + vis_margins, vis_pos[1] + vis_margins))
    screen.blit(vis_pieces, (vis_pos[0] + vis_margins, vis_pos[1] + vis_margins))

if __name__ == "__main__":
    pygame.init()
    init()
    
    screen = pygame.display.set_mode([800, 600])
    clock = pygame.time.Clock() 
    running = True

    while running:
        event = pygame.event.poll()
     
        if event.type == pygame.QUIT:
            running = False
        else:
            update(event)

            screen.fill((100, 100, 100))  
            draw(screen)
            pygame.display.flip()

    pygame.quit()
    

