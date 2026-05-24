from fastapi import APIRouter, WebSocket, status
from utils.security import get_current_user
from websocket.connection_manager import manager

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        current_user = await get_current_user(token)
        email = current_user["sub"]
    except:
        await websocket.close(code=1008)
        return

    await websocket.accept()  # <- chỉ gọi 1 lần ở đây
    await manager.connect(email, websocket)

    try:
        while True:
            _ = await websocket.receive_text()
    except:
        manager.disconnect(email, websocket)