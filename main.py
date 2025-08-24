
import logging
import pathlib
from Client.player import Player
from Game.game import Game
from Game.PieceFactory import PieceFactory
from Game.publisher_factory import PublisherFactory,create_board
from Game.img import Img


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    white_player = Player("white",50)
    black_player = Player("black",1000)
    pub = PublisherFactory(white_player,black_player)
    board = create_board()

    publisher = pub.init_publisher()
    pf = PieceFactory(board,publisher._publisher)
    pf.generate_library(pathlib.Path(__file__).parent / "pieces")
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
    Game(pieces, board,publisher,white_player,black_player,pf).run()


