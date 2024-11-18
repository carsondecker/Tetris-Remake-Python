import random
from constants import *
from tetromino import Tetromino

class Board:
    def __init__(self):
        self.grid = np.empty((BOARD_HEIGHT, BOARD_WIDTH), dtype=object)
        self.last_rotation = False  # Track if last move was a rotation
        self.last_kick_index = 0    # Track which kick was used in last rotation
        self.back_to_back = -1
        self.combo = -1  # Start at -1 so first clear gives combo of 0
        self.garbage_queued = 0
        
    def is_valid_position(self, x, y):
        return (0 <= x < BOARD_WIDTH) and (0 <= y < BOARD_HEIGHT)
    
    def check_collision(self, piece, dx=0, dy=0):
        shape_height, shape_width = np.shape(piece.shape)

        # Loop through all minos and check if they can move to the new location
        for x in range(shape_width):
            for y in range(shape_height):
                if piece.shape[y, x]:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    
                    if not self.is_valid_position(new_x, new_y):
                        return True
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
        
        blocked_corners = sum(
            1 for x, y in corners
            if not self.is_valid_position(x, y) or self.grid[y, x] is not None
        )
        
        if blocked_corners < 3:
            return None
        
        front_corners = None
        if piece.rotation_state == 0:  # Facing up
            front_corners = corners[:2]
        elif piece.rotation_state == 1:  # Facing right
            front_corners = [corners[1], corners[3]]
        elif piece.rotation_state == 2:  # Facing down
            front_corners = corners[2:]
        elif piece.rotation_state == 3:  # Facing left
            front_corners = [corners[0], corners[2]]
        
        front_corner_check = any(
            self.is_valid_position(x, y) and self.grid[y, x] is None
            for x, y in front_corners
        )

        if self.last_kick_index < 4 and front_corner_check:
            return "MINI T-SPIN"
        return "T-SPIN"

    def is_perfect_clear(self):
        return not np.any(self.grid != None)

    def check_lines(self, piece):
        lines_cleared = []

        min_y = max(0, piece.y)
        max_y =  min(BOARD_HEIGHT - 1, piece.y + len(piece.shape))
        
        for y in range(min_y, max_y + 1):
            if all(cell is not None for cell in self.grid[y]):
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
            if clear_type in ["TETRIS", "T-SPIN SINGLE", "T-SPIN DOUBLE", "T-SPIN TRIPLE", "MINI T-SPIN SINGLE"]:
                self.back_to_back += 1
            else:
                self.back_to_back = -1
        else:
            if self.garbage_queued != 0:
                self.add_garbage_lines(self.garbage_queued)
                self.garbage_queued = 0
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
        for line in lines:
            self.grid = np.vstack([np.full(BOARD_WIDTH, None), self.grid])

    def add_garbage_lines(self, num):
        self.grid = np.delete(self.grid, range(num), axis=0)
        for i in range(num):
            row = np.empty(BOARD_WIDTH, dtype=object)
            hole = random.randint(0, BOARD_WIDTH - 1)
            for j in range(BOARD_WIDTH):
                if j != hole:
                    row[j] = GRAY
            self.grid = np.vstack([self.grid, row])
            
    def garbage_calc(self, clear_dict):
        if not clear_dict or clear_dict['lines'] == 0:
            return 0

        # Attack & Combo Table taken from jstris
        attack_table = {
            'SINGLE': 0,
            'DOUBLE': 1,
            'TRIPLE': 2,
            'TETRIS': 4,
            'T-SPIN DOUBLE': 4,
            'T-SPIN TRIPLE': 6,
            'T-SPIN SINGLE': 2,
            'T-SPIN MINI SINGLE': 0
        }

        lines_sent = 0
        if clear_dict['clear_type']:
            lines_sent += attack_table[clear_dict['clear_type']]
        if clear_dict['perfect_clear']:
            lines_sent += 10
        if clear_dict['back_to_back'] > 0:
            lines_sent += 1
        
        combo = clear_dict['combo']
        if combo > 1:
            if combo < 5:
                lines_sent += 1
            elif combo < 7:
                lines_sent += 2
            elif combo < 9:
                lines_sent += 3
            elif combo < 12:
                lines_sent += 4
            else:
                lines_sent += 5

        return lines_sent

    def take_garbage(self, num):
        self.garbage_queued += num

    def send_garbage(self, num):
        if num <= self.garbage_queued:
            self.garbage_queued -= num
            return 0
        
        sent = num - self.garbage_queued
        self.garbage_queued = 0
        return sent

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