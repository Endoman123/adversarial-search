from player import *
from board import Board
from minimax import *
import pygame
import pygame_gui as gui
from pygame import *
from pygame.locals import *

window_size = (800, 600)

vis_ui = None
vis_board = None
vis_overlay = None
vis_pieces = None

vis_pos = (10, 10)
vis_bwidth = 580
vis_margins = 0
vis_gutters = 5
vis_csize = -1

pnl_main = None
btn_fow = None
win_init = None

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
debug = False

# Class just to easily make a "New Game" dialog
class UINewDialog(gui.elements.UIWindow):  
    _cur_difficulty = 4
    _cur_size = 2

    def __init__(self, location, manager, window_title = "New Game", object_id = gui.core.ObjectID(object_id='#new_dialog', class_id=None)):
        super().__init__(rect=pygame.Rect(location, (640, 480)), 
                         manager=manager, 
                         window_display_title=window_title,
                         element_id=None, 
                         object_id=object_id, 
                         resizable=True,
                         visible=True)

        btn_layout_rect = pygame.Rect(0, 0, 100, 20)
        btn_layout_rect.bottomright = (-30, -20)

        # Bottom right anchor
        anc_br = {'left': 'right', 'right': 'right', 'top': 'bottom', 'bottom': 'bottom'}

        # Top left anchor
        anc_tl = {'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'}
        
        # Top justify anchor
        anc_tj = {'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}

        dd_choices = [repr(x) for x in range(1, 6)]

        self._btn_confirm = gui.elements.UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                     text="Start",
                                     manager=self.ui_manager,
                                     container=self,
                                     object_id='#btn_confirm',
                                     anchors=anc_br)

        self._btn_cancel = gui.elements.UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                     text="Cancel",
                                     manager=self.ui_manager,
                                     container=self,
                                     object_id='#btn_confirm',
                                     anchors=anc_br)

        self._dd_difficulty = gui.elements.ui_drop_down_menu.UIDropDownMenu(options_list=dd_choices,
                                                                            starting_option="4",
                                                                            relative_rect=pygame.Rect(160, 10, 100, 20),
                                                                            manager=self.ui_manager,
                                                                            container=self,
                                                                            anchors=anc_tj)

        self._dd_size = gui.elements.ui_drop_down_menu.UIDropDownMenu(options_list=dd_choices,
                                                                      starting_option="2",
                                                                      relative_rect=pygame.Rect(160, 50, 100, 20),
                                                                      manager=self.ui_manager,
                                                                      container=self,
                                                                      anchors=anc_tj)

        self._lbl_difficulty = gui.elements.UILabel(relative_rect=pygame.Rect(10, 10, 140, 20),
                                                    text="Difficulty: ",
                                                    manager=self.ui_manager,
                                                    container=self,
                                                    parent_element=self._dd_difficulty,
                                                    anchors=anc_tl)
        
        self._lbl_size = gui.elements.UILabel(relative_rect=pygame.Rect(10, 50, 140, 20),
                                                    text="Size: ",
                                                    manager=self.ui_manager,
                                                    container=self,
                                                    parent_element=self._dd_size,
                                                    anchors=anc_tl)
        self.set_blocking(True)

    def process_event(self, event: pygame.event.Event) -> bool: 
        consumed_event = super().process_event(event)


        if (event.type == pygame.USEREVENT and event.user_type == gui.UI_DROP_DOWN_MENU_CHANGED):
            if event.ui_element == self._dd_difficulty:
                self._cur_difficulty = int(event.text)
            if event.ui_element == self._dd_size:
                self._cur_size = int(event.text)

        if (event.type == pygame.USEREVENT and event.user_type == gui.UI_BUTTON_PRESSED):
            if (event.ui_element == self._btn_cancel):
                self.kill()

            if (event.ui_element == self._btn_confirm):
                event_data = {'user_type': gui.UI_CONFIRMATION_DIALOG_CONFIRMED,
                              'difficulty': int(self._cur_difficulty),
                              'size': int(self._cur_size),
                              'ui_element': self,
                              'ui_object_id': self.most_specific_combined_id}

                new_event = pygame.event.Event(pygame.USEREVENT, event_data)
                pygame.event.post(new_event)
                self.kill()

        return consumed_event

def init(board_mult, difficulty):
    global vis_board, vis_overlay, vis_csize, vis_pieces, btn_fow, sprites, board, p1, p2
    
    board = Board(board_mult)
    board_size = len(board)
    
    vis_csize = vis_bwidth - vis_margins - vis_gutters * (board_size - 1)
    vis_csize //= board_size 
    vis_owidth = vis_bwidth - vis_margins * 2

    vis_board = Surface((vis_bwidth, vis_bwidth))
    vis_board.fill((0, 0, 0))

    vis_overlay = Surface((vis_owidth, vis_owidth), pygame.SRCALPHA)
    vis_pieces = Surface((vis_owidth, vis_owidth), pygame.SRCALPHA)


    for x in range(board_size):
        for y in range(board_size):
            color = (50, 50, 50) if board[y][x] != "O" else (50, 20, 0)
                
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
    
    p1 = GUIPlayer(board, True, vis_pos, vis_csize, vis_margins, vis_gutters)  
    p2 = MMPlayer(board, False, difficulty, h = h_advantage)

def build_ui():
    global btn_fow, btn_init, win_init

    btn_init = gui.elements.UIButton(relative_rect=pygame.Rect((600, 40), (190, 30)),
                                     text='New Game',
                                     manager=vis_ui)

    btn_fow = gui.elements.UIButton(relative_rect=pygame.Rect((600, 10), (190, 30)),
                                    text='Toggle FOW',
                                    manager=vis_ui)

    lbl_obs = None # gui.elements.UILabel()

def update(dt):
    global cur_turn, running
 
    if cur_turn: 
        move = p1.get_move()

        if move:
            board.move(move[0], move[1])
            cur_turn = False 
    else:
        move = p2.get_move()

        if len(move) != 2:
            raise Exception(move)

        board.move(move[0], move[1])
        cur_turn = True

    # Check for end state
    state = board.create_memento()
    a_count = sum(map(lambda x: x in "WHM", state))
    b_count = sum(map(lambda x: x in "whm", state))

    if a_count == 0 or b_count == 0:
        running = False

def process_event(ev):
    global debug, running

    if ev.type == pygame.QUIT:
        running = False
        return

    if ev.type == pygame.USEREVENT:
        if ev.user_type == gui.UI_BUTTON_PRESSED: 
            if ev.ui_element == btn_fow:
                board.toggle_fow()    
            if ev.ui_element == btn_init:
                UINewDialog(location=(10, 10),
                            manager=vis_ui)

        if ev.user_type == gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
           d = ev.difficulty
           s = ev.size

           init(s, d)

    elif ev.type == KEYUP:
        if ev.key == pygame.K_d:
            debug = not debug
            vis_ui.set_visual_debug_mode(debug)
    elif cur_turn and ev.type == pygame.MOUSEBUTTONUP and ev.button == 1: # If the left mouse button is pressed
        p1.consume_event(ev)
        
def draw(screen): 
    vis_overlay.convert_alpha()
    vis_overlay.fill(0) 

    vis_pieces.convert_alpha()
    vis_pieces.fill(0) 

    # Two different flows for rendering:
    # one with FOW, one without FOW
    if board.get_fow(): 
        team = "WHM" if p1.get_major() else "whm"

        for x in range(len(board)):
            for y in range(len(board)):
                p = board[y][x] 
                x_pos = x * vis_csize + x * vis_gutters - x
                y_pos = y * vis_csize + y * vis_gutters - y
                
                if p in team and sprites[p]:
                    vis_pieces.blit(sprites[p], (x_pos, y_pos))
                else:
                    c_fow = (40, 40, 40)
                    pygame.draw.rect(vis_overlay, c_fow, (x_pos, y_pos, vis_csize, vis_csize))
        
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
    
                x_pos = x * vis_csize + x * vis_gutters - x
                y_pos = y * vis_csize + y * vis_gutters - y
                
                pygame.draw.rect(vis_overlay, color, (x_pos, y_pos, vis_csize, vis_csize))    

    else:
        for x in range(len(board)):
            for y in range(len(board)):
                p = board[y][x] 
                x_pos = x * vis_csize + x * vis_gutters - x
                y_pos = y * vis_csize + y * vis_gutters - y
                
                if p not in "_O" and sprites[p]:
                    vis_pieces.blit(sprites[p], (x_pos, y_pos))

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
    
    screen.blit(vis_board, vis_pos) 
    screen.blit(vis_overlay, (vis_pos[0] + vis_margins, vis_pos[1] + vis_margins))
    screen.blit(vis_pieces, (vis_pos[0] + vis_margins, vis_pos[1] + vis_margins))

if __name__ == "__main__":
    pygame.init()
    
    screen = pygame.display.set_mode(window_size)
    vis_ui = gui.UIManager(window_size)
    clock = pygame.time.Clock() 
    running = True

    build_ui()
    init(2, 5)

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get(): 
            vis_ui.process_events(event) 
            process_event(event)

            
        update(dt)
        screen.fill((0, 0, 0))  
        draw(screen)

        vis_ui.update(dt) 
        vis_ui.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()
    

