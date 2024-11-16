import random
from constants import *

class Tetromino:
    def __init__(self, piece_name: str):
        # Get all basic piece information
        self.rotation_state = 0
        self.piece_name = piece_name
        self.piece, self.color = PIECES[piece_name]
        self.piece = np.copy(self.piece)

        # Set starting position #CHANGE TO 0-whatever NUMBERING
        if piece_name in ['I', 'O']:
            self.x = BOARD_WIDTH // 2 - len(self.piece[0]) // 2
        else:
            self.x = BOARD_WIDTH // 2 - len(self.piece[0]) // 2 - 1
        self.y = 21 # The bottom of each piece is on row 1

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
            self.piece = np.rot90(self.piece, -1)
        else:
            new_rotation = (self.rotation_state +-1) % 4
            self.piece = np.rot90(self.piece, -1)

        # Kicking
        kick_data = self.get_wall_kick_data(self.rotation_state * 2 + (1 if clockwise else 0))

        # Check each new position and move there if it works
        for kick_x, kick_y in kick_data:
            if not board.check_collision(self, kick_x, kick_y):
                self.x += kick_x
                self.y += kick_y
                self.rotation_state = new_rotation
                return True
        return False
    
    def move(self, board, dx, dy):
        if not board.check_collision(self, dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False