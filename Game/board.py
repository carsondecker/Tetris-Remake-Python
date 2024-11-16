from constants import *
from tetromino import Tetromino

class Board:
    def __init__(self):
        self.grid = np.empty((BOARD_HEIGHT, BOARD_WIDTH), dtype=object)
        self.last_rotation = False  # Track if last move was a rotation
        self.last_kick_index = 0    # Track which kick was used in last rotation
        self.score = 0
        self.back_to_back = 0
        self.combo = -1  # Start at -1 so first clear gives combo of 0
        
    def is_valid_position(self, x, y):
        return 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT
    
    def check_collision(self, piece, dx=0, dy=0):
        shape_height, shape_width = np.shape(piece.shape)

        # Loop through all minos and check if they can move to the new location
        for x in range(shape_width):
            for y in range(shape_height):
                if piece.shape[y, x]:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    
                    print(self.is_valid_position(new_x, new_y))
                    if not self.is_valid_position(new_x, new_y):
                        return True
                    print(self.grid[new_y, new_x])
                    if self.grid[new_y, new_x] is not None:
                        return True
        return False
    
    def add_to_board(self, piece):
        shape_height, shape_width = np.shape(piece.shape)

        # Add each mino to the board
        for x in range(shape_width):
            for y in range(shape_height):
                if piece.shape[y,x]:
                    self.grid[piece.y + y, piece.x + x] = piece.color

    def is_t_spin(self, piece):
        if piece.piece_name != 'T' or not self.last_rotation:
            return None
        
        center_x = piece.x + 1
        center_y = piece.y + 1
        corners = [
            (center_x - 1, center_y - 1),
            (center_x + 1, center_y - 1),
            (center_x - 1, center_y + 1),
            (center_x + 1, center_y + 1)
        ]
        
        blocked_corners = 0
        front_corners = 0
        for i, (x, y) in enumerate(corners):
            if not self.is_valid_position(x, y) or (self.grid[y, x] is not None):
                blocked_corners += 1
                if i < 2:
                    front_corners += 1
        
        if blocked_corners >= 3:
            return "T-SPIN"
        elif blocked_corners >= 2 and front_corners == 2:
            return "MINI T-SPIN"
        return None

    def is_perfect_clear(self):
        return not np.any(self.grid != None)

    def check_lines(self, piece):
        lines_cleared = []
        
        min_y = max(0, piece.y)
        max_y = min(BOARD_HEIGHT, piece.y + len(piece.shape))
        
        for y in range(min_y, max_y):
            if np.all(self.grid[y] != None):
                lines_cleared.append(y)
        
        clear_type = None
        if lines_cleared:
            tspin_type = self.is_t_spin(piece)
            if tspin_type == "T-SPIN":
                if len(lines_cleared) == 1:
                    clear_type = "T-SPIN SINGLE"
                elif len(lines_cleared) == 2:
                    clear_type = "T-SPIN DOUBLE"
                elif len(lines_cleared) == 3:
                    clear_type = "T-SPIN TRIPLE"
            elif tspin_type == "MINI T-SPIN":
                if len(lines_cleared) == 1:
                    clear_type = "MINI T-SPIN SINGLE"
                else:
                    clear_type = "MINI T-SPIN"
            else:
                if len(lines_cleared) == 1:
                    clear_type = "SINGLE"
                elif len(lines_cleared) == 2:
                    clear_type = "DOUBLE"
                elif len(lines_cleared) == 3:
                    clear_type = "TRIPLE"
                elif len(lines_cleared) == 4:
                    clear_type = "TETRIS"
        
        if lines_cleared:
            self.combo += 1
            if clear_type in ["TETRIS", "T-SPIN SINGLE", "T-SPIN DOUBLE", "T-SPIN TRIPLE"]:
                self.back_to_back += 1
            else:
                self.back_to_back = 0
        else:
            self.combo = -1
            
        if lines_cleared:
            self.remove_lines(lines_cleared)
            perfect_clear = self.is_perfect_clear()
            
            return {
                'clear_type': clear_type,
                'lines': len(lines_cleared),
                'perfect_clear': perfect_clear,
                'combo': max(0, self.combo),
                'back_to_back': self.back_to_back
            }
            
        return None

    def remove_lines(self, lines):
        lines.sort(reverse=True)
        
        for line in lines:
            self.grid = np.delete(self.grid, line, axis=0)
            self.grid = np.vstack([np.full(BOARD_WIDTH, None), self.grid])

    def draw(self, screen, current_piece=None):
        # Grid
        for x in range(BOARD_OFFSET_X, BOARD_WIDTH * CELL_SIZE + BOARD_OFFSET_X + 1, CELL_SIZE):
           pygame.draw.line(
               screen,
               BOARD_LINE,
               (x, BOARD_OFFSET_Y),
               (x, GRID_HEIGHT * CELL_SIZE + BOARD_OFFSET_Y)
           )
        
        # Draw horizontal grid lines
        for y in range(BOARD_OFFSET_Y, GRID_HEIGHT * CELL_SIZE + BOARD_OFFSET_Y + 1, CELL_SIZE):
            pygame.draw.line(
                screen,
                BOARD_LINE,
                (BOARD_OFFSET_X, y),
                (BOARD_WIDTH * CELL_SIZE + BOARD_OFFSET_X, y)
            )
        
        pygame.draw.rect(screen, BOARD_BORDER, pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_WIDTH * CELL_SIZE + 1, GRID_HEIGHT * CELL_SIZE + 1), 1)

        # Pieces on board
        for x in range(BOARD_WIDTH):
            for y in reversed(range(BOARD_HEIGHT)):
                if self.grid[y, x]:
                    pygame.draw.rect(screen, self.grid[y, x],
                        (BOARD_OFFSET_X + x * CELL_SIZE,
                        BOARD_OFFSET_Y + (y - GRID_HEIGHT) * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE))