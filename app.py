from player import *
from board import Board
import pygame
from pygame.locals import *

board = None
p1 = None
p2 = None
p1_move = None
p2_move = None
cur_turn = None
running = False

def update(delta):
    global running

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False

def draw(delta, screen):
    screen.fill((100, 100, 100))

if __name__ == "__main__":
    board = Board(3)
    p1 = CLIPlayer(board, True)
    p2 = AIPlayer(board, False, 4)

    pygame.init()
    
    screen = pygame.display.set_mode([800, 600])
    clock = pygame.time.Clock() 
    running = True

    while running:
        dt = clock.tick(60) 
        
        update(dt)
        draw(dt, screen)
        pygame.display.flip()

    pygame.quit()
    

