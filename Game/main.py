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
        self.drop_speed = 50
        self.last_drop_time = pygame.time.get_ticks()
        self.lock_delay = 500  # Time in ms before piece locks
        self.last_move_time = 0
        self.lock_time = 0
        
        # DAS
        self.das_delay = 170
        self.das_speed = 50
        self.last_key_down_time = 0
        self.moving_direction = 0
        
        self.fill_next_queue()

    def fill_next_queue(self):
        if len(self.next_pieces) <= 7:
            bag = list(PIECES.keys())
            random.shuffle(bag)
            self.next_pieces.extend(bag)
        if not self.current_piece:
            self.spawn_piece()

    def spawn_piece(self):
        if not self.current_piece:
            self.current_piece = Tetromino(self.next_pieces.pop(0))
            self.fill_next_queue()
        
        if self.board.check_collision(self.current_piece):
            self.game_over = True
            return False
        return True
    
    def hold_piece(self):
        if self.can_hold:
            if self.held_piece:
                temp = self.held_piece
                self.held_piece = self.current_piece
                self.current_piece = temp
                self.held_piece.x = self.held_piece.original_x
                self.held_piece.y = self.held_piece.original_y
            else:
                self.held_piece = self.current_piece
                self.held_piece.x = self.held_piece.original_x
                self.held_piece.y = self.held_piece.original_y
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
            if current_time - self.last_key_down_time >= self.das_delay:
                if current_time - self.last_move_time >= self.das_speed:
                    self.current_piece.move(self.board, self.moving_direction, 0)
                    self.last_move_time = current_time

    def draw(self):
        self.screen.fill(BLACK)
        
        self.current_piece.draw(self.screen)
        self.current_piece.draw_ghost(self.screen, self.ghost_surface, self.board)
        self.board.draw(self.screen)
    
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False 
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    
                    if not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.moving_direction = -1
                            self.last_key_down_time = pygame.time.get_ticks()
                            if self.current_piece:
                                self.current_piece.move(self.board, -1, 0)
                        
                        elif event.key == pygame.K_RIGHT:
                            self.moving_direction = 1
                            self.last_key_down_time = pygame.time.get_ticks()
                            if self.current_piece:
                                self.current_piece.move(self.board, 1, 0)
                        
                        elif event.key == pygame.K_UP:
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
                    self.moving_direction = 0
    
    def update(self):
        while self.running:
            self.clock.tick(FPS)
            
            if not self.paused and not self.game_over:
                current_time = pygame.time.get_ticks()
                
                # Handle DAS movement
                self.handle_das()
                
                # Handle piece dropping
                if current_time - self.last_drop_time > self.drop_speed:
                    if self.current_piece:
                        if not self.board.check_collision(self.current_piece, 0, 1):
                            self.current_piece.move(self.board, 0, 1)
                            self.lock_time = current_time
                        elif current_time - self.lock_time >= self.lock_delay:
                            self.lock_piece()
                    self.last_drop_time = current_time
                
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