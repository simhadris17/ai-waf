import logging

from fastapi import WebSocket

logger = logging.getLogger("ai-waf.ws")


class ConnectionManager:
    def __init__(self):
        self._clients: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._clients.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self._clients:
            self._clients.remove(websocket)

    async def broadcast(self, data: dict):
        dead = []
        for client in self._clients:
            try:
                await client.send_json(data)
            except Exception:
                dead.append(client)
        for client in dead:
            self.disconnect(client)


manager = ConnectionManager()
