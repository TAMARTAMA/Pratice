from Components.publisher import Publisher

from Components.game_messages import GameMessages
from Components.sound_effects import SoundEffects
from Game.Board import Board

from Game.img import Img
import pathlib
def create_board() -> Board:
    board_img = Img().read(
        pathlib.Path(__file__).parent / "board.jpg",
        size=(1280, 740),  
        keep_aspect=False
    )

    offset_x = 300
    offset_y = 100
    cell_size = 80    # 640 / 8 = 80
    amount_cells = 8
    return Board(cell_size,cell_size,offset_x, offset_y, amount_cells, amount_cells, board_img)

sounds = SoundEffects()
messages = GameMessages()

from Client.player import Player
class PublisherFactory:   
    def __init__(self,player_w_:Player,player_b_:Player):
        self.player_w,self.player_b =player_w_,player_b_
        self._publisher = Publisher()
    def init_publisher(self)->"PublisherFactory":
        
        
        self._publisher.subscribe("piece_captured_W",self.player_w.score.on_capture)
        self._publisher.subscribe("piece_captured_B", self.player_b.score.on_capture)
        self._publisher.subscribe("piece_captured_history_W", self.player_w.history.on_captured)
        self._publisher.subscribe("piece_captured_history_B", self.player_b.history.on_captured)

        self._publisher.subscribe("piece_moved_W", self.player_w.history.on_move)
        self._publisher.subscribe("piece_moved_B", self.player_b.history.on_move)

        self._publisher.subscribe("piece_moved_sound", sounds.on_piece_moved)
        self._publisher.subscribe("piece_captured_sound", sounds.on_piece_captured)
        self._publisher.subscribe("move_rejected_sound", sounds.on_move_rejected)
        self._publisher.subscribe("on_piece_jump_sound", sounds.on_piece_jump)

        self._publisher.subscribe("game/start", messages.on_game_start)
        self._publisher.subscribe("game/end", messages.on_game_end)

        return self
    def add_score_to_board(self,board:Board):
        self.player_w.score.draw_on(board.img.img, x=20, y=60)
        self.player_b.score.draw_on(board.img.img, x=1000, y=60)


    def add_messages_to_board(self,board:Board):    
        messages.draw_on(board.img.img, x=400, y=50)
    def add_move_history_to_board(self,board:Board):    
        self.player_w.history.draw_on(board.img.img)
        self.player_b.history.draw_on(board.img.img)

