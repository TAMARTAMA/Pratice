
import asyncio
import websockets
import json
from dataclasses import dataclass
from typing import List, Dict
from dataclasses import asdict
@dataclass
class Command:
    timestamp: int
    piece_id: str
    type: str
    params: List

clients: Dict[str, websockets.WebSocketServerProtocol] = {}
queue = asyncio.Queue()

async def handler(websocket, path):
    # הרשמה של השחקן לפי צבע
    if "white" not in clients:
        player_color = "white"
    elif "black" not in clients:
        player_color = "black"
    else:
        await websocket.send(json.dumps({"error": "game full"}))
        await websocket.close()
        return

    clients[player_color] = websocket
    await websocket.send(json.dumps({"info": f"{player_color}"}))
    print(f"{player_color} joined")

    # אם שני שחקנים מחוברים – התחל משחק
    if len(clients) == 2 and not hasattr(handler, "game_started"):
        asyncio.create_task(run_game_loop())
        handler.game_started = True
        await broadcast({"info": "Game started"})

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("type") == "command":
                command_data = data["data"]

                # המרה של כל איבר ב־params ל־tuple (כדי שיהיה hashable)
                if "params" in command_data:
                    command_data["params"] = [tuple(p) for p in command_data["params"]]
                    

                command = Command(**command_data)
                await queue.put((player_color, command))


    except websockets.exceptions.ConnectionClosed:
        print(f"{player_color} disconnected")
        del clients[player_color]

async def broadcast(message: dict):
    for color, ws in clients.items():
        if ws.open:
            await ws.send(json.dumps(message))

async def run_game_loop():
    print("[LOOP] Game loop started")
    while True:
        sender_color, command = await queue.get()
        receiver_color = "black" if sender_color == "white" else "white"
        if receiver_color in clients and clients[receiver_color].open:
            await clients[receiver_color].send(json.dumps({
                "type": "command",
                 "data": asdict(command)
            }))

async def main():
    async with websockets.serve(handler, "localhost", 8000):
        print("Server started on ws://localhost:8000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
