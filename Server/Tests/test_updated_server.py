import asyncio
import pytest
import websockets
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game_manager import RealTimeChessServer
from Game.game_factory import create_game_instance

# Port נפרד בשביל טסט
TEST_PORT = 9876

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def start_server():
    server = RealTimeChessServer(None)
    server_task = asyncio.create_task(
        websockets.serve(server.handler, "localhost", TEST_PORT)
    )
    await asyncio.sleep(0.5)  # זמן לשרת לעלות
    yield server
    server_task.cancel()

@pytest.mark.asyncio
async def test_join_creates_game_instance(start_server):
    uri = f"ws://localhost:{TEST_PORT}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "join", "game_id": "game-123"}))
        await asyncio.sleep(0.5)  # זמן לשרת לטפל
        assert "game-123" in start_server.games
        game = start_server.games["game-123"]
        assert hasattr(game, "run")  # נוודא שהמשחק הוא מופע תקני

@pytest.mark.asyncio
async def test_command_sent_to_right_game(start_server):
    uri = f"ws://localhost:{TEST_PORT}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "join", "game_id": "game-456"}))
        await asyncio.sleep(0.2)

        test_cmd = {
            "type": "command",
            "command": {"piece_id": "KW", "dst": [6, 4]}  # פקודת דוגמה
        }
        await ws.send(json.dumps(test_cmd))
        await asyncio.sleep(0.2)

        game = start_server.games["game-456"]
        assert not game.user_input_queue.empty()
        cmd = game.user_input_queue.get()
        assert cmd.piece_id == "KW"
        assert cmd.dst == (6, 4)
