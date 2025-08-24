
from Game.Command import Command
from Game.State import State
import cv2

class Piece:
    def __init__(self, piece_id: str, init_state: State):
        self.id = piece_id
        self.state = init_state

    def on_command(self, cmd: Command, now_ms: int):
        if self.state.can_transition(now_ms):
            self.state.reset(cmd)
            self.state = self.state.get_state_after_command(cmd, now_ms)

    def reset(self, start_ms: int):
        self.state.reset(Command(start_ms, self.id, "Idle", []))

    def update(self, now_ms: int):
        self.state = self.state.update(now_ms)


    def draw_on_board(self, board, now_ms: int):
        x, y = self.state.physics.get_pos()
        sprite = self.state.graphics.get_img()
        sprite.draw_on(board.img, x, y)  

        remain = self.state.cooldown_end_ms - now_ms
        if remain > 0:
            secs = remain / 1000.0
            cv2.putText(board.img.img, f"{secs:0.1f}",
                        (x + 4, y + 16),  
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,  
                        (0, 0, 255, 255), 1, cv2.LINE_AA)  

