# game_factory.py

from Game.game import Game
from Client.player import Player
from Game.publisher_factory import PublisherFactory
from Game.PieceFactory import PieceFactory
from Game.publisher_factory import create_board
import pathlib

def create_game_instance(game_id: str):
    white_player = Player("white", 50)
    black_player = Player("black", 1000)

    pub = PublisherFactory(white_player, black_player)
    board = create_board()
    publisher = pub.init_publisher()

    pf = PieceFactory(board, publisher._publisher)
    pf.generate_library(pathlib.Path(__file__).parent / "pieces")

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
        if isinstance(cells, tuple):
            cells = [cells]
        for cell in cells:
            pieces.append(pf.create_piece(code, cell))

    game = Game(pieces, board, publisher, white_player, black_player, pf)
    return game
