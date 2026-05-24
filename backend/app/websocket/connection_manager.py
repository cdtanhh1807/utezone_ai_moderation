from typing import Dict, List
from fastapi import WebSocket
from models.message_model import Message
import json

class ConnectionManager:
    _connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, email: str, websocket: WebSocket):
        if email not in self._connections:
            self._connections[email] = []
        self._connections[email].append(websocket)

    def disconnect(self, email: str, websocket: WebSocket):
        self._connections[email] = [
            ws for ws in self._connections.get(email, []) if ws != websocket
        ]
        if not self._connections[email]:
            del self._connections[email]

    async def send_personal_message(self, message: Message):
        sockets = self._connections.get(message.receiver_email, [])
        for ws in sockets:
            await ws.send_text(json.dumps(message.dict(), default=str))

    async def send_json(self, payload: dict, receiver: str):
        """Gửi bất kỳ dict nào (conversation_update, ...)"""
        sockets = self._connections.get(receiver, [])
        for ws in sockets:
            await ws.send_text(json.dumps(payload, default=str))

manager = ConnectionManager()