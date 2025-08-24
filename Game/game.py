import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from Game.logic import _is_win,_resolve_collisions,_announce_win,_process_input,_validate
from Game.Board   import Board
from Game.Command import Command
from Components.score_board import ScoreBoard
from Game.Piece   import Piece
from Game.img     import Img
from Game.publisher_factory import PublisherFactory
from dataclasses import asdict
from Game.PieceFactory import PieceFactory
from Client.player import Player
class InvalidBoard(Exception): ...
import asyncio
import websockets
import json
import json
class Game:
    def __init__(self, pieces: List[Piece], board: Board,publisher:PublisherFactory,player:Player
                 ,pf:PieceFactory,websocket=None):
        if not _validate(pieces):
            raise InvalidBoard("duplicate pieces or no king")

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)  # להפוך אותו ל־current בתוך thread זה
        self.pieces           = pieces
        self.board            = board
        self.START_NS         = time.monotonic_ns()
        self.user_input_queue = queue.Queue()   
        # self.user_input_queue_other = asyncio.Queue()        
        self.selected_id: Optional[str] = None         

        self.pos            : Dict[Tuple[int, int], Piece] = {}
        self.piece_by_id    : Dict[str, Piece] = {p.id: p for p in pieces}

        self._player = player

        self.publisher = publisher
        self.pf = pf
        self.loop = None
        self.websocket = websocket
        # self.game_id = game_id
        

    def game_time_ms(self) -> int:
        return (time.monotonic_ns() - self.START_NS) // 1_000_000

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        img_copy = Img()
        img_copy.img = self.board.img.img.copy()
        return Board(self.board.cell_H_pix, self.board.cell_W_pix,
             self.board.offset_x,
             self.board.offset_y,
             self.board.W_cells, self.board.H_cells,
             img_copy)


    def _mouse_cb(self, event, x, y, flags, userdata):
        event_is_down = event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN)
        if not event_is_down:
            return

        is_jump = (event == cv2.EVENT_RBUTTONDOWN)

        cell = ((y-self.board.offset_y) // self.board.cell_H_pix, (x-self.board.offset_x) // self.board.cell_W_pix)

        if self.selected_id is None:  
            piece = self.pos.get(cell)
            if piece:
                self.selected_id = piece.id
        else:
            cmd_type = "jump" if is_jump else "move"
            cmd = Command(self.game_time_ms(),
                          self.selected_id,
                          cmd_type,
                          [cell])
            self.user_input_queue.put(cmd)

            self.selected_id = None
    
    def start_user_input_thread(self):

        cv2.namedWindow("Kung-Fu Chess")
        cv2.setMouseCallback("Kung-Fu Chess", self._mouse_cb)
    async def send_command_to_server(self, cmd: Command):
        if not self.websocket:
            print("WebSocket not connected.")
            return

        try:
           await self.websocket.send(json.dumps({
                "type": "command",
                "data": asdict(cmd)  # data הוא dict – מצוין!
            }))

        except Exception as e:
            print(f"Failed to send command: {e}")

    def _send_command(self, cmd):
        self.send_command_to_server(cmd)

    def run(self):
        self.publisher._publisher.publish("game/start","")
        self._draw() 
        self._show()
        # await asyncio.sleep(2)
        time.sleep(2) 

        self.start_user_input_thread()
        start_ms = self.game_time_ms()

        for p in self.pieces:
            p.reset(start_ms)
        while not _is_win(self.pieces):
            now = self.game_time_ms()

            for p in self.pieces:
                p.update(now)
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                # שליחה לשרת
                self.loop.call_soon_threadsafe(
                    asyncio.create_task,
                    self.send_command_to_server(cmd)
                )



                
                time.sleep(1)
                _process_input(cmd,self.piece_by_id,self.game_time_ms(),self.pos)


            self._draw()
            if not self._show():   
                break
            _resolve_collisions(self.pieces)
            
        self.publisher._publisher.publish("game/end",_announce_win(self.pieces))
        self._draw() 
        self._show()
        time.sleep(2)    
        # await asyncio.sleep(2)
        cv2.destroyAllWindows()

    def _draw(self):
        self.curr_board = self.clone_board()
        self.pos.clear()
        for p in self.pieces:
            p.draw_on_board(self.curr_board, now_ms=self.game_time_ms())
            self.pos[p.state.physics.start_cell] = p

    def _show(self) -> bool:
        self.publisher.add_score_to_board(self.curr_board)
        self.publisher.add_messages_to_board(self.curr_board)
        self.publisher.add_move_history_to_board(self.curr_board)
        cv2.imshow("Kung-Fu Chess", self.curr_board.img.img)
        
        key = cv2.waitKey(1) & 0xFF
        return key != 27




    

    


