from typing import Dict, List
from fastapi import WebSocket

class ChannelWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: str):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append(websocket)
        print(f"[WS] Connected to channel {channel_id}, total: {len(self.active_connections[channel_id])}")

    def disconnect(self, websocket: WebSocket, channel_id: str):
        if channel_id in self.active_connections:
            if websocket in self.active_connections[channel_id]:
                self.active_connections[channel_id].remove(websocket)
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
        print(f"[WS] Disconnected from channel {channel_id}")

    async def broadcast(self, channel_id: str, message: dict):
        if channel_id in self.active_connections:
            print(f"[BROADCAST] channel {channel_id} has {len(self.active_connections[channel_id])} connections")
            for conn in self.active_connections[channel_id]:
                try:
                    await conn.send_json(message)
                    print(f"[BROADCAST] sent to {conn}")
                except Exception as e:
                    print(f"[BROADCAST] error: {e}")
        else:
            print(f"[BROADCAST] channel {channel_id} not in active_connections")

ws_manager = ChannelWebSocketManager()