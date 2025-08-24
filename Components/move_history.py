import time
from typing import List, Tuple
import cv2
from Game.Command import Command
class MoveHistory:
    def __init__(self,name,offset=50):
        self.moves: List[str] = []  
        self.max_moves = 10
        self.ofsset = offset
        self.name = name
        

    def on_move(self, cmd: Command):
        now = time.time()
        move_str = cmd.type + str(cmd.params[0]) + "  " + str(int(now))
        self.moves.append(move_str)

        self.moves = self.moves[-self.max_moves:] 
    def on_captured(self, cmd: Command):
        now = time.time()
        self.moves.append(cmd.type +str(cmd.params[0])+ "x"+ "  " + str(int(now)))
        self.moves = self.moves[-self.max_moves:]     

    def draw_on(self, img ):
        for i, msg in enumerate(reversed(self.moves)):
            y_offset = 100 + i * 30
            cv2.putText(img, msg, (self.ofsset, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)
