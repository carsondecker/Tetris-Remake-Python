import random
from constants import *

class Tetromino:
    def __init__(self, piece_name):
        # Get all basic piece information
        self.rotation_state = 0
        self.piece_name = piece_name
        self.shape, self.color = PIECES[piece_name]
        self.shape = np.copy(self.shape)