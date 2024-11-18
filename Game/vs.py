import multiprocessing
import pygame
import random
from game import Game
from constants import *

class MultiplayerMessage:
    QUIT = "QUIT"
    RESTART = "RESTART"
    GARBAGE = "GARBAGE"
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data

# Add Multiplayer functionality to the game by extending the Game class
class MultiplayerGame(Game):
    def __init__(self, conn, seed):
        super().__init__(conn, seed)

    def lock_piece(self):
        if self.current_piece:
            self.board.add_to_board(self.current_piece)
            clear_result = self.board.check_lines(self.current_piece)
            if clear_result:
                lines_sent = self.board.send_garbage(self.board.garbage_calc(clear_result))
                if lines_sent > 0:
                    try:
                        self.conn.send(MultiplayerMessage(MultiplayerMessage.GARBAGE, lines_sent))
                    except (EOFError, BrokenPipeError):
                        self.running = False
            self.current_piece = None
            self.can_hold = True
            self.spawn_piece()

    def handle_broad_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.conn.send(MultiplayerMessage("QUIT"))
                self.running = False 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                        self.conn.send(MultiplayerMessage("RESTART"))
                        self.restart_game()
                elif event.key == pygame.K_p:
                        self.paused = not self.paused

    def handle_connection(self):
        try:
            if self.conn.poll():
                message = self.conn.recv()
                if isinstance(message, MultiplayerMessage):
                    if message.type == MultiplayerMessage.QUIT:
                        self.running = False
                    elif message.type == MultiplayerMessage.RESTART:
                        self.restart_game()
                    elif message.type == MultiplayerMessage.GARBAGE:
                        self.board.take_garbage(message.data)
        except (EOFError, BrokenPipeError):
            self.running = False

    def update(self):
        super().update()
        self.handle_connection()

def run_game(conn, seed):
    game = MultiplayerGame(conn, seed)
    try:
        game.run()
    except Exception as e:
        print(e)
        try:
            conn.send(MultiplayerMessage(MultiplayerMessage.QUIT))
        except (EOFError, BrokenPipeError):
            pass
        finally:
            conn.close()
            pygame.quit()

class MultiplayerVS:
    def __init__(self):
        # Create bidirectional pipes for both players
        self.p1_conn, self.p2_conn = multiprocessing.Pipe()
        
        self.seed = random.randint(0, 2**32 - 1)
        
        # Create and start game processes
        self.p1_process = multiprocessing.Process(target=run_game, args=(self.p1_conn, self.seed))
        self.p2_process = multiprocessing.Process(target=run_game, args=(self.p2_conn, self.seed))
        
        self.p1_process.start()
        self.p2_process.start()
    
    def run(self):
        try:
            self.p1_process.join()
            self.p2_process.join()
        except KeyboardInterrupt:
            self.p1_conn.send(MultiplayerMessage(MultiplayerMessage.QUIT))
            self.p2_conn.send(MultiplayerMessage(MultiplayerMessage.QUIT))
            self.p1_process.terminate()
            self.p2_process.terminate()
        finally:
            self.p1_conn.close()
            self.p2_conn.close()

if __name__ == "__main__":
    multiplayer_game = MultiplayerVS()
    multiplayer_game.run()