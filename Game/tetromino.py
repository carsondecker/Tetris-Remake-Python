from constants import *

class Tetromino:
    def __init__(self, piece_name: str):
        # Get all basic piece information
        self.rotation_state = 0
        self.piece_name = piece_name
        self.shape, self.color = PIECES[piece_name]
        self.shape = np.copy(self.shape)
        self.last_kick_index = 0

        # Set starting position
        if piece_name in ['I', 'O']:
            self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2
        else:
            self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2 - 1
        self.y = 18 # +Y goes down

    def get_wall_kick_tests(self, old_state, new_state):
        if self.piece_name == 'O':
            return [(0, 0)]
        
        kick_type = 'I' if self.piece_name == 'I' else 'JLSTZ'
        
        if old_state == 0 and new_state == 1:  # 0>>1
            test_index = 0
        elif old_state == 1 and new_state == 0:  # 1>>0
            test_index = 1
        elif old_state == 1 and new_state == 2:  # 1>>2
            test_index = 2
        elif old_state == 2 and new_state == 1:  # 2>>1
            test_index = 3
        elif old_state == 2 and new_state == 3:  # 2>>3
            test_index = 4
        elif old_state == 3 and new_state == 2:  # 3>>2
            test_index = 5
        elif old_state == 3 and new_state == 0:  # 3>>0
            test_index = 6
        elif old_state == 0 and new_state == 3:  # 0>>3
            test_index = 7
        else:
            return [(0, 0)]
        
        return WALL_KICK_DATA[kick_type][test_index]
    
    def rotate(self, board, clockwise=True):
        if self.piece_name == 'O':
            return True
            
        old_state = self.rotation_state
        new_state = (old_state + (1 if clockwise else 3)) % 4
        
        # Store original position and shape
        original_x = self.x
        original_y = self.y
        original_shape = self.shape.copy()
        
        # Rotate the shape
        self.shape = np.rot90(self.shape, -1 if clockwise else 1)
        
        # Try basic rotation first
        if not board.check_collision(self):
            self.rotation_state = new_state
            board.last_rotation = True
            board.last_kick_index = 0
            return True
        
        # Get and try wall kicks
        kick_tests = self.get_wall_kick_tests(old_state, new_state)
        
        for i, (kick_x, kick_y) in enumerate(kick_tests):
            self.x = original_x + kick_x
            self.y = original_y - kick_y  # Negative because kicks use opposite Y direction
            
            if not board.check_collision(self):
                self.rotation_state = new_state
                board.last_rotation = True
                board.last_kick_index = i
                return True
                
            # Reset position for next kick test
            self.x = original_x
            self.y = original_y
        
        # If no kicks worked, restore original state
        self.shape = original_shape
        self.x = original_x
        self.y = original_y
        self.rotation_state = old_state
        return False
    
    def move(self, board, dx, dy):
        if not board.check_collision(self, dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False
    
    def get_ghost_position(self, board):
        ghost_y = 0
        while not board.check_collision(self, 0, ghost_y + 1):
            ghost_y += 1
        return ghost_y + self.y
    
    def draw(self, screen, offset_x=None, offset_y=None, preview=False):
        if preview:
            # Draw piece in next queue or hold
            shape_height, shape_width = np.shape(self.shape)
            for x in range(shape_width):
                for y in range(shape_height):
                    if self.shape[y, x]:
                        pygame.draw.rect(screen, self.color,
                            (offset_x + x * CELL_SIZE, 
                            offset_y + y * CELL_SIZE,
                            CELL_SIZE, CELL_SIZE))
        else:
            # Draw piece on board
            shape_height, shape_width = np.shape(self.shape)
            for x in range(shape_width):
                for y in reversed(range(shape_height)):
                    if self.shape[y, x]:
                        pygame.draw.rect(screen, self.color,
                            (BOARD_OFFSET_X + (self.x + x) * CELL_SIZE,
                            BOARD_OFFSET_Y + (self.y + y - GRID_HEIGHT) * CELL_SIZE,
                            CELL_SIZE, CELL_SIZE))

    def draw_ghost(self, screen, ghost_surface, board):
        # Clear the ghost surface
        ghost_surface.fill((0,0,0,0))
        
        # Get ghost position
        ghost_y = self.get_ghost_position(board)
        
        # Draw ghost piece onto the surface
        ghost_color = (*self.color, 128)
        shape_height, shape_width = np.shape(self.shape)
        
        for x in range(shape_width):
            for y in reversed(range(shape_height)):
                if self.shape[y, x]:
                    pygame.draw.rect(
                        ghost_surface,
                        ghost_color,
                        ((self.x + x) * CELL_SIZE,
                         (ghost_y + y) * CELL_SIZE,
                         CELL_SIZE, CELL_SIZE)
                    )
        
        # Draw the ghost surface to the screen
        screen.blit(
            ghost_surface,
            (BOARD_OFFSET_X, BOARD_OFFSET_Y - GRID_HEIGHT * CELL_SIZE)
        )