import asyncio
import websockets
import json

class GameClient:
    def __init__(self):
        self.state = {}

    async def run(self):
        async with websockets.connect("ws://localhost:8765") as websocket:
            receiver = asyncio.create_task(self.listen(websocket))
            sender = asyncio.create_task(self.send_moves(websocket))
            await asyncio.gather(receiver, sender)

    async def listen(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "init":
                print("Initial state:", data["state"])
                self.state = data["state"]
            elif data["type"] == "update":
                print("Updated state:", data["state"])
                self.state = data["state"]

    async def send_moves(self, websocket):
        while True:
            await asyncio.sleep(3)  # לצורך הדגמה - כל 3 שניות תנועה מזויפת
            move = {"from": "a2", "to": "a3", "piece": "PW"}
            await websocket.send(json.dumps({"type": "move", "move": move}))

if __name__ == "__main__":
    asyncio.run(GameClient().run())
