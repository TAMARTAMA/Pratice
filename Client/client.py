# client.py
import pathlib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Game.game import Game
from Game.PieceFactory import PieceFactory
from Game.publisher_factory import PublisherFactory,create_board
from Client.player import Player
import websockets
import json
import asyncio
import websockets
from typing import List

from Game.Command import Command
game = None
def init_board(websocket)->Game:
    white_player = Player("f","white")
    black_player = Player("fg","black")
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
    return Game(pieces, board,publisher,white_player,pf,websocket)



async def send_command_to_server(self, cmd: Command):
    if not self.websocket:
        print("WebSocket not connected.")
        return

    try:
        await self.websocket.send(cmd.to_json())  # או json.dumps(cmd.__dict__) אם את לא משתמשת ב- to_json
    except Exception as e:
        print(f"Failed to send command: {e}")


from Game.logic import _process_input
# פונקציה סינכרונית שמעבדת את הפקודה
def handle_command_sync(cmd: Command):
    
    _process_input(cmd, game.piece_by_id, game.game_time_ms(), game.pos)
    print(f"[SYNC] Got command: {cmd}")
async def listen(ws):

    async for message in ws:
        try:
            data = json.loads(message)
            print("[SERVER]", data)
            data = json.loads(message)

            if data.get("type") == "command":
                command_data = data["data"]
                if "params" in command_data:
                    command_data["params"] = [tuple(p) for p in command_data["params"]]
                command = Command(**command_data)
                handle_command_sync(command)
                
        except Exception as e:
            print("Error receiving:", e)

async def main():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:

        first = await websocket.recv()
        print("[SERVER INIT]", first)
        color_player = json.loads(first).get("info")

        global game 
        game = init_board(websocket)
        loop = asyncio.get_event_loop()
        game.loop = loop
        loop.run_in_executor(None, game.run)

        await asyncio.gather(
            listen(websocket),
            
        )


        


if __name__ == "__main__":
    asyncio.run(main())


