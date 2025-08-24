from Components.score_board import ScoreBoard
from Components.move_history import MoveHistory
from Game.Command import Command
import websockets
offset = {
    "white":50,
    "black" :1000
}
class Player:
    def __init__(self,name , color: str, ip:str="192.168.0.1",websocket :websockets=None):
        self.color = color  # "white" or "black"
        self.score = ScoreBoard(color)
        self.history = MoveHistory(color,offset.get(color))
        self.won = False

        self.ip = ip
        self.name = name

        self.websocket = websocket
        

    def record_move(self, cmd:Command):
       self.history.on_move(cmd)

    def on_capture(self, value):
        self.score.on_capture(value)

    def set_win(self):
        self.won = True

    def __str__(self):
        return f"{self.color} | נקודות: {self.score} | מהלכים: {len(self.move_history)}"
