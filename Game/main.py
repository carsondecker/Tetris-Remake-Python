import pygame
import sys
import numpy as np
import random

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # Cyan (I)
    (0, 0, 255),    # Blue (J)
    (255, 128, 0),  # Orange (L)
    (255, 255, 0),  # Yellow (O)
    (0, 255, 0),    # Green (S)
    (128, 0, 128),  # Purple (T)
    (255, 0, 0)     # Red (Z)
]

# Game Constants
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
FPS = 60

SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH + 1
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT + 1

class Tetromino:
    def __init__():
        pass

class Grid:
    def __init__(self):
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the grid and its contents."""
        # Draw vertical grid lines
        for x in range(0, GRID_WIDTH * CELL_SIZE + 1, CELL_SIZE):
            pygame.draw.line(
                screen,
                GRAY,
                (x, 0),
                (x, GRID_HEIGHT * CELL_SIZE)
            )
        
        # Draw horizontal grid lines
        for y in range(0, GRID_HEIGHT * CELL_SIZE + 1, CELL_SIZE):
            pygame.draw.line(
                screen,
                GRAY,
                (0, y),
                (GRID_WIDTH * CELL_SIZE, y)
            )
        

class Game:
    def __init__(self):
        pygame.init()

        # Display setup
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")

        self.grid = Grid()

        # Game state
        self.running = False
        self.clock = pygame.time.Clock()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.grid.draw(self.screen)
        
        #Update display
        pygame.display.flip()

    def run(self) -> None:
        self.running = True
        self.update()
    
    def update(self) -> None:
        while self.running:
            self.handle_events()
            self.screen.fill(BLACK)
            self.grid.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()