from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from meeting.websocket.meeting_manager import meeting_manager
from meeting.services.meeting_service import meeting_service
from services.other.file_service import FileService
from utils.security import get_current_user
import json
import httpx  # Thêm để gọi API nội bộ

router = APIRouter(tags=["meeting-websocket"])

async def get_fullname_from_api(email: str, token: str) -> str:
    """Gọi API account_info để lấy fullName giống frontend"""
    try:
        # Gọi API nội bộ - điều chỉnh URL nếu cần
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/account/account_info?email={email}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("fullName") or email.split('@')[0]
    except Exception as e:
        print(f"Error fetching fullName from API: {e}")
    
    # Fallback: dùng phần trước @ của email
    return email.split('@')[0]

@router.websocket("/ws/meeting/{room_id}")
async def meeting_websocket(websocket: WebSocket, room_id: str, token: str = Query(...)):
    try:
        current_user = await get_current_user(token)
        email = current_user["sub"]
        # ===== SỬA: Gọi API lấy fullName thay vì dùng từ token =====
        full_name = await get_fullname_from_api(email, token)
        username = full_name  # Dùng fullName làm username
    except:
        await websocket.close(code=1008)
        return
    
    socket_id = str(id(websocket))
    
    can_join, error, room = await meeting_service.can_join(room_id, email)
    if not can_join:
        await websocket.close(code=1008, reason=error)
        return
    
    await websocket.accept()
    await meeting_manager.connect_to_room(room_id, email, websocket)
    
    existing = any(p.email == email for p in room.participants)
    if existing:
        await meeting_service.update_socket_id(room_id, email, socket_id)
    else:
        await meeting_service.add_participant(room_id, email, username, socket_id)
    
    await meeting_manager.broadcast_to_room(room_id, {
        "type": "user_joined",
        "email": email,
        "username": username,  # ===== SỬA: Gửi fullName thay vì email =====
        "socket_id": socket_id
    }, exclude_email=email)
    
    # ===== SỬA: Lấy fullName cho tất cả participants =====
    participants_info = []
    for p in room.participants:
        if p.email != email:
            # Nếu participant đã có username (fullName) thì dùng, 
            # nếu chưa thì gọi API lấy (hoặc dùng tạm email)
            participant_fullname = p.username if p.username and p.username != p.email else p.email.split('@')[0]
            participants_info.append({
                "email": p.email,
                "username": participant_fullname,  # ===== SỬA: Đảm bảo là fullName =====
                "is_host": p.is_host,
                "audio_on": p.audio_on,
                "video_on": p.video_on
            })
    
    await websocket.send_text(json.dumps({
        "type": "joined_room",
        "room_id": room_id,
        "room_type": room.room_type,
        "is_host": room.host_email == email,
        "participants": participants_info,
        "whiteboard": room.whiteboard_data,
        "scheduled_at": room.scheduled_at.isoformat() if room.scheduled_at else None
    }, default=str))
    
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type")
            
            if msg_type == "offer":
                target_email = msg.get("target")
                await meeting_manager.send_to_user(room_id, target_email, {
                    "type": "offer",
                    "from": email,
                    "offer": msg.get("offer")
                })
            
            elif msg_type == "answer":
                target_email = msg.get("target")
                await meeting_manager.send_to_user(room_id, target_email, {
                    "type": "answer",
                    "from": email,
                    "answer": msg.get("answer")
                })
            
            elif msg_type == "ice_candidate":
                target_email = msg.get("target")
                await meeting_manager.send_to_user(room_id, target_email, {
                    "type": "ice_candidate",
                    "from": email,
                    "candidate": msg.get("candidate")
                })
            
            elif msg_type == "media_toggle":
                audio = msg.get("audio")
                video = msg.get("video")
                await meeting_service.update_media_status(room_id, socket_id, audio, video)
                
                await meeting_manager.broadcast_to_room(room_id, {
                    "type": "media_toggle",
                    "email": email,
                    "audio": audio,
                    "video": video
                }, exclude_email=email)
            
            elif msg_type == "chat":
                content = msg.get("content")
                msg_type_chat = msg.get("msg_type", "text")
                
                saved_msg = await meeting_service.save_message(
                    room_id=room_id,
                    sender_email=email,
                    sender_name=username,  # ===== SỬA: Lưu fullName vào DB =====
                    message_type=msg_type_chat,
                    content=content,
                    file_name=msg.get("file_name") if msg_type_chat != "text" else None,
                    file_size=msg.get("file_size") if msg_type_chat != "text" else None
                )
                
                response = {
                    "type": "chat",
                    "sender_email": email,
                    "sender_name": username, 
                    "msg_type": msg_type_chat,
                    "content": content,
                    "file_url": saved_msg.get("file_url"),
                    "file_name": saved_msg.get("file_name"),
                    "timestamp": saved_msg["created_at"].isoformat()
                }
                
                await meeting_manager.broadcast_to_room(room_id, response)
            
            elif msg_type == "whiteboard_draw":
                await meeting_manager.broadcast_to_room(room_id, {
                    "type": "whiteboard_draw",
                    "from": email,
                    "data": msg.get("data")
                }, exclude_email=email)
            
            elif msg_type == "whiteboard_clear":
                await meeting_manager.broadcast_to_room(room_id, {
                    "type": "whiteboard_clear",
                    "from": email
                }, exclude_email=email)
            
            elif msg_type == "whiteboard_save":
                canvas_data = msg.get("canvas")
                await meeting_service.save_whiteboard(room_id, canvas_data)
            
            elif msg_type == "end_room":
                if room.host_email == email:
                    result = await meeting_service.end_room(room_id, email)
                    await meeting_manager.broadcast_to_room(room_id, {
                        "type": "room_ended",
                        "by": email,
                        "deleted_files": result.get("deleted_files", 0)
                    })
                    
                    for e, ws in list(meeting_manager.rooms.get(room_id, {}).items()):
                        if e != email:
                            await ws.close()
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Only host can end room"
                    }))
            
            elif msg_type == "leave":
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Meeting WebSocket error: {e}")
    finally:
        await meeting_manager.disconnect_from_room(websocket)
        closed = await meeting_service.remove_participant(room_id, socket_id)
        
        if not closed:
            await meeting_manager.broadcast_to_room(room_id, {
                "type": "user_left",
                "email": email,
                "socket_id": socket_id
            })