import pygame
import sys
import random
from board import Board
from tetromino import Tetromino
from constants import *

class Game:
    def __init__(self, conn, seed):
        pygame.init()
        
        self.conn = conn
        self.seed = seed
        self.piece_generator = random.Random(seed)

        # Display setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")

        # Create single ghost surface for all pieces
        self.ghost_surface = pygame.Surface((BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), pygame.SRCALPHA)
        
        self.initialize_game_state()
        
        self.clock = pygame.time.Clock()
        self.running = False

    def initialize_game_state(self):
        self.board = Board()
        self.current_piece = None
        self.next_pieces = []
        self.held_piece = None
        self.can_hold = True
        
        self.paused = False
        self.game_over = False
        self.lines_cleared = 0
        
        self.gravity = .02
        self.gravity_count = 0
        self.last_drop_time = pygame.time.get_ticks()
        self.lock_delay = 500
        self.last_move_time = 0
        self.lock_time = 0
        
        # Handling
        self.sdf = 1000
        self.das = 125
        self.arr = 0
        self.is_soft_dropping = False
        self.last_key_down_time = 0
        self.moving_direction = 0
        self.reset_das = False
        
        self.fill_next_queue()

    def restart_game(self):
        self.initialize_game_state()

    def fill_next_queue(self):
        if len(self.next_pieces) <= 7:
            bag = list(map(lambda x: Tetromino(x), PIECES.keys()))
            self.piece_generator.shuffle(bag)
            self.next_pieces.extend(bag)
        if not self.current_piece:
            self.spawn_piece()

    def spawn_piece(self):
        if not self.current_piece:
            self.current_piece = self.next_pieces.pop(0)
            self.fill_next_queue()
        
        if self.board.check_collision(self.current_piece):
            self.game_over = True
            return False
        return True
    
    def hold_piece(self):
        if self.can_hold:
            if self.held_piece:
                temp = self.held_piece
                self.held_piece = Tetromino(self.current_piece.piece_name)
                self.current_piece = temp
            else:
                self.held_piece = self.current_piece
                self.current_piece = None
                self.held_piece = Tetromino(self.held_piece.piece_name)
                self.spawn_piece()
            self.can_hold = False
    
    def lock_piece(self):
        if self.current_piece:
            self.board.add_to_board(self.current_piece)
            self.board.check_lines(self.current_piece)
            self.current_piece = None
            self.can_hold = True
            self.spawn_piece()
    
    def hard_drop(self):
        if self.current_piece:
            drop_distance = 0
            while not self.board.check_collision(self.current_piece, 0, drop_distance + 1):
                drop_distance += 1
            
            if drop_distance > 0:
                self.current_piece.move(self.board, 0, drop_distance)
            self.lock_piece()
    
    def handle_das(self):
        if self.moving_direction != 0:
            current_time = pygame.time.get_ticks()

            if self.reset_das:
                self.last_key_down_time = current_time
                self.reset_das = False

            if current_time - self.last_key_down_time >= self.das:
                if current_time - self.last_move_time >= self.arr:
                    self.current_piece.move(self.board, self.moving_direction, 0)
                    self.last_move_time = current_time

    def draw_preview_piece(self, piece, starting_x, starting_y, width, height):
        piece.draw(self.screen, starting_x + ((width - len(piece.shape[0]) * CELL_SIZE) // 2), 
                   starting_y + ((height - (3 if piece.piece_name == 'I' else 2) * CELL_SIZE) // 2), True)

    def draw_hold(self):
        pygame.draw.rect(self.screen, BOARD_BORDER, (BOARD_OFFSET_X - SIDEBAR_OFFSET - SIDEBAR_WIDTH, BOARD_OFFSET_Y, SIDEBAR_WIDTH, PREVIEW_PIECE_HEIGHT), 1)
        if self.held_piece:
            self.draw_preview_piece(self.held_piece, BOARD_OFFSET_X - SIDEBAR_OFFSET - SIDEBAR_WIDTH, BOARD_OFFSET_Y, SIDEBAR_WIDTH, PREVIEW_PIECE_HEIGHT)

    def draw_next_queue(self):
        pygame.draw.rect(self.screen, BOARD_BORDER, (BOARD_OFFSET_X + BOARD_WIDTH * CELL_SIZE + SIDEBAR_OFFSET, BOARD_OFFSET_Y, SIDEBAR_WIDTH, PREVIEW_PIECE_HEIGHT * 5), 1)
        for i in range(5):
            self.draw_preview_piece(self.next_pieces[i], BOARD_OFFSET_X + (BOARD_WIDTH * CELL_SIZE + 1) + SIDEBAR_OFFSET,
                                     BOARD_OFFSET_Y + PREVIEW_PIECE_HEIGHT * i, SIDEBAR_WIDTH, PREVIEW_PIECE_HEIGHT)

    def draw(self):
        self.screen.fill(BLACK)
        
        self.board.draw(self.screen)
        self.current_piece.draw(self.screen)
        self.current_piece.draw_ghost(self.screen, self.ghost_surface, self.board)
        self.draw_hold()
        self.draw_next_queue()
    
        pygame.display.flip()

    def handle_ingame_events(self, events):
        keys = pygame.key.get_pressed()
        self.is_soft_dropping = keys[pygame.K_DOWN]
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if not self.paused:
                        if event.key == pygame.K_LEFT:
                            if self.moving_direction == 1:
                                self.reset_das = True
                            self.moving_direction = -1
                            self.last_key_down_time = pygame.time.get_ticks()
                            if self.current_piece:
                                self.current_piece.move(self.board, -1, 0)
                        
                        elif event.key == pygame.K_RIGHT:
                            if self.moving_direction == -1:
                                self.reset_das = True
                            self.moving_direction = 1
                            self.last_key_down_time = pygame.time.get_ticks()
                            if self.current_piece:
                                self.current_piece.move(self.board, 1, 0)
                        
                        elif event.key == pygame.K_UP or event.key == pygame.K_x:
                            if self.current_piece:
                                self.current_piece.rotate(self.board)
                                # Last rotation isn't true if the piece can fall more because of the way t-spins are calculated
                                if self.current_piece.get_ghost_position(self.board) == self.current_piece.y:
                                    self.board.last_rotation = True
                                else:
                                    self.board.last_rotation = False
                        
                        elif event.key == pygame.K_z:
                            if self.current_piece:
                                self.current_piece.rotate(self.board, False)
                                # Last rotation isn't true if the piece can fall more because of the way t-spins are calculated
                                if self.current_piece.get_ghost_position(self.board) == self.current_piece.y:
                                    self.board.last_rotation = True
                                else:
                                    self.board.last_rotation = False
                        
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                        
                        elif event.key == pygame.K_c:
                            self.hold_piece()
            
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    if (event.key == pygame.K_LEFT and self.moving_direction == -1) or \
                       (event.key == pygame.K_RIGHT and self.moving_direction == 1):
                        self.moving_direction = 0
    
    # Separated from ingame events because they need to be done differently in multiplayer
    def handle_broad_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                        self.restart_game()
                elif event.key == pygame.K_p:
                        self.paused = not self.paused

    def handle_events(self):
        events = pygame.event.get()
        self.handle_broad_events(events)
        self.handle_ingame_events(events)

    def update(self):
        self.clock.tick(FPS)

        if not self.paused and not self.game_over:
            current_time = pygame.time.get_ticks()
            # Handle DAS movement
            self.handle_das()
            
            if self.current_piece:
                current_gravity = self.gravity * (self.sdf if self.is_soft_dropping else 1)

                self.gravity_count += current_gravity
                cells_to_drop = int(self.gravity_count)
                
                if cells_to_drop > 0:
                    self.gravity_count -= cells_to_drop
                    
                    # Try to drop the piece by the calculated amount
                    actual_drop = 0
                    for i in range(cells_to_drop):
                        if not self.board.check_collision(self.current_piece, 0, 1):
                            self.current_piece.move(self.board, 0, 1)
                            actual_drop += 1
                        else:
                            break
                    
                    # If we couldn't drop at all, start lock delay
                    if actual_drop == 0 and current_time - self.lock_time >= self.lock_delay:
                        self.lock_piece()
                    elif actual_drop > 0:
                        self.lock_time = current_time
                
        self.handle_events()
        self.draw()

    def run(self):
        self.running = True
        while self.running:
            self.update()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    seed = random.randint(0, 2**32 - 1)
    game = Game(None, seed)
    game.run()