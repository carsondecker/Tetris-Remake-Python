import pygame
import sys
import random
from board import Board
from tetromino import Tetromino
from constants import *

class Game:
    def __init__(self):
        pygame.init()
        
        # Display setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")

        # Create single ghost surface for all pieces
        self.ghost_surface = pygame.Surface((BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), pygame.SRCALPHA)
        
        self.board = Board()
        self.current_piece = None
        self.next_pieces = []
        self.held_piece = None
        self.can_hold = True
        
        self.running = False
        self.paused = False
        self.game_over = False
        self.lines_cleared = 0
        
        self.clock = pygame.time.Clock()
        self.gravity = .02 # In 'G', where 1G is moving down 1 cell per frame
        self.gravity_count = 0
        self.last_drop_time = pygame.time.get_ticks()
        self.lock_delay = 500  # Time in ms before piece locks
        self.last_move_time = 0
        self.lock_time = 0
        
        # Handling
        self.sdf = 1000 # * Gravity (1000 is instant for .02G)
        self.das = 125 # ms
        self.arr = 0 # ms
        self.is_soft_dropping = False
        self.last_key_down_time = 0
        self.moving_direction = 0
        self.reset_das = False
        
        self.fill_next_queue()

    def fill_next_queue(self):
        if len(self.next_pieces) <= 7:
            bag = list(map(lambda x: Tetromino(x), PIECES.keys()))
            random.shuffle(bag)
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

    def handle_events(self):
        keys = pygame.key.get_pressed()
        self.is_soft_dropping = keys[pygame.K_DOWN]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    
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
                                self.board.last_rotation = True
                        
                        elif event.key == pygame.K_z:
                            if self.current_piece:
                                self.current_piece.rotate(self.board, False)
                                self.board.last_rotation = True
                        
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                        
                        elif event.key == pygame.K_c:
                            self.hold_piece()
            
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    if (event.key == pygame.K_LEFT and self.moving_direction == -1) or \
                       (event.key == pygame.K_RIGHT and self.moving_direction == 1):
                        self.moving_direction = 0
    
    def update(self):
        while self.running:
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
                
                # Handle events and update display
                self.handle_events()
                self.draw()
                
                # Handle events and update display
                self.handle_events()
                self.draw()
            
            else:
                self.handle_events()
                self.draw()
        
        pygame.quit()
        sys.exit()

    def run(self):
        self.running = True
        self.update()


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()