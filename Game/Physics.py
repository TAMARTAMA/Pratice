from typing import Tuple, Optional
from Game.Command import Command
import math
from Components.publisher import Publisher
class Physics:
    SLIDE_CELLS_PER_SEC = 4.0

    def __init__(self, start_cell: Tuple[int, int],
                 board: "Board", speed_m_s: float = 1.0,publisher=Publisher):
        self.board = board
        self.start_cell = start_cell
        self.end_cell = start_cell
        self.speed = speed_m_s
        self.start_ms = 0
        self.last_square = start_cell
        self.wait_only = False
        self.publisher = publisher
        self._captured=False

    def reset(self, cmd: Command):

        dest_cell = cmd.params[0] if cmd.params else self.start_cell
        print(f"[Physics.reset] from {self.start_cell} to {dest_cell}")
        self.mode = cmd.type
        self.end_cell   = dest_cell                
        self.start_ms   = cmd.timestamp
        self.last_square = self.start_cell

        dy = self.end_cell[0] - self.start_cell[0]
        dx = self.end_cell[1] - self.start_cell[1]
        dist_cells = math.hypot(dx, dy)
        self.wait_only = (
                dist_cells == 0
                and cmd.type != "Idle"
        )
        self.duration_ms = max(200,              
            dist_cells / self.SLIDE_CELLS_PER_SEC * 1000)
        if cmd.type == "move":
            self.publisher.publish("piece_moved_sound", "move")
            self.publisher.publish("piece_moved", cmd)
        else:
            if cmd.type == "jump":
                self.publisher.publish("on_piece_jump_sound", "jump")
            elif cmd.type == "idle":
                self.publisher.publish("move_rejected_sound", "error")


    def add_history(self,fun:str ,cmd):
        self.publisher.publish(fun, cmd)
    def update(self, now_ms: int):
        if self.start_cell == self.end_cell and not self.wait_only:
            return None                  

        dur = self.duration_ms
        t   = min(1.0, (now_ms - self.start_ms) / dur)

        if self.mode == "Jump":

            height_px = 30                
            arc_y = -4 * height_px * (t - 0.5) ** 2 + height_px
        else:
            arc_y = 0

        sy, sx = self.start_cell
        ey, ex = self.end_cell
        cur_row = sy + (ey - sy) * t
        cur_col = sx + (ex - sx) * t
        cur_square = (int(round(cur_row)), int(round(cur_col)))
        if cur_square != self.last_square:
            print(f"[TRACE] entering {cur_square}")
            self.last_square = cur_square


        self.curr_px_f = (cur_col * self.board.cell_W_pix+self.board.offset_x,
                          cur_row * self.board.cell_H_pix - arc_y+self.board.offset_y)
        self.curr_px   = (round(self.curr_px_f[0]), round(self.curr_px_f[1]))
        
        if t >= 1.0:
            self.start_cell = self.end_cell
            self.wait_only = False
            return Command(now_ms, "?", "Arrived", [])
        
        return None

    def get_pos(self) -> Tuple[int, int]:
        """
        Current pixel-space upper-left corner of the sprite.
        Uses the sub-pixel coordinate computed in update();
        falls back to the square’s origin before the first update().
        """
        return getattr(self, "curr_px",
                       (self.start_cell[1] * self.board.cell_W_pix+self.board.offset_x,
                        self.start_cell[0] * self.board.cell_H_pix+self.board.offset_y))

    def captured(self) : 

        self.publisher.publish("piece_captured_sound", "piece_captured")
        self._captured = True
         
    def in_captured(self,player_fun="piece_captured_W",data={},cmd:Command= None) :    
        self.publisher.publish(player_fun, data)
        self.publisher.publish("piece_captured_history_"+player_fun[-1],cmd)

    def can_be_captured(self)->bool:
        return self._captured
        

