
from typing import Dict, Optional

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Game.game import Game
from Client.player import Player
import pathlib
from Game.PieceFactory import PieceFactory
from Game.publisher_factory import PublisherFactory,create_board
from Game.PieceFactory import PieceFactory
from Game.publisher_factory import PublisherFactory,create_board

class GameServer:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: Dict[str, Player] = {}
        self.game:Game = None
        self.start = False

    def add_player(self, name: str, ip: str) -> Optional[str]:
        if "white" not in self.players:
            self.players["white"] = Player(name, "white", ip)
            self.start = True
            return "white"
        elif "black" not in self.players:
            self.players["black"] = Player(name, "black", ip)
            
            return "black"
        else:
            return None  # המשחק מלא

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameServer] = {}

    def add_or_get_game(self, game_id: str) -> Game:
        if game_id not in self.games:
            self.games[game_id] = GameServer(game_id)
        if self.games[game_id].start:
            self.games[game_id].game =self.init_board
            (game_id,self.games[game_id].players["white"],self.games[game_id].players["black"])
            
        return self.games[game_id]


    def init_board(self,game_id:str,white_player:Player,black_player:Player):
        pub = PublisherFactory(white_player,black_player)
        board = create_board()

        publisher = pub.init_publisher()
        pf = PieceFactory(board,publisher._publisher)
        pf.generate_library(pathlib.Path(__file__).parent.parent / "pieces")
        #TODO read_csv
        initial_setup = {
            "RW": [(7, 0), (7, 7)], "RB": [(0, 0), (0, 7)],
            "NW": [(7, 1), (7, 6)], "NB": [(0, 1), (0, 6)],
            "BW": [(7, 2), (7, 5)], "BB": [(0, 2), (0, 5)],
            "QW": (7, 3), "QB": (0, 3),
            "KW": (7, 4), "KB": (0, 4),
            "PW": [(6, c) for c in range(8)],
            "PB": [(1, c) for c in range(8)],
        }
        
        pieces = []
        for code, cells in initial_setup.items():
            if isinstance(cells, tuple):  # single square
                cells = [cells]
            for cell in cells:
                pieces.append(pf.create_piece(code, cell))
        print("Pieces on board:", [p.id for p in pieces])
        return Game(game_id,pieces, board,publisher,white_player,black_player,pf)
    def get_game_summary(self) -> Dict[str, Dict[str, str]]:
        """החזרת מבט על כל המשחקים והשחקנים"""
        summary = {}
        for game_id, game in self.games.items():
            summary[game_id] = {
                color: player.name for color, player in game.players.items()
            }
        return summary
    def run_game(self, game_id):
        if game_id in self.games:
            self.games[game_id].game.run()



