from constants import *

class Tetromino:
    def __init__(self, piece_name: str):
        # Get all basic piece information
        self.rotation_state = 0
        self.piece_name = piece_name
        self.shape, self.color = PIECES[piece_name]
        self.shape = np.copy(self.shape)

        # Set starting position
        if piece_name in ['I', 'O']:
            self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2
        else:
            self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2 - 1
        self.y = 18 # +Y goes down

        self.original_x = self.x
        self.original_y = self.y

    def get_wall_kick_data(self, rotation):
        if self.piece_name == 'I':
            return WALL_KICK_DATA['I'][rotation]
        elif self.piece_name != 'O':
            return WALL_KICK_DATA['JLSTZ'][rotation]
        return [(0,0)]
    
    def rotate(self, board, clockwise=True):
        # Rotate piece
        if self.piece_name == 'O':
            return True

        if clockwise:
            new_rotation = (self.rotation_state + 1) % 4
            self.shape = np.rot90(self.shape, -1)
        else:
            new_rotation = (self.rotation_state -1) % 4
            self.shape = np.rot90(self.shape, 1)

        # Kicking
        kick_data = self.get_wall_kick_data(self.rotation_state * 2 + (1 if clockwise else 0))

        # Check each new position and move there if it works
        for kick_x, kick_y in kick_data:
            if not board.check_collision(self, kick_x, kick_y):
                self.x += kick_x
                self.y += kick_y
                self.rotation_state = new_rotation
                return True
            
        if clockwise:
            self.shape = np.rot90(self.shape, 1)
        else:
            self.shape = np.rot90(self.shape, -1)
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