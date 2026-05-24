from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from meeting.services.meeting_service import meeting_service
from services.other.file_service import FileService  # Dùng FileService sẵn có
from utils.security import get_current_user
from meeting.models.meeting_model import RoomSettings

router = APIRouter(prefix="/meetings", tags=["meetings"])

class CreateRoomRequest(BaseModel):
    room_type: str = "instant"  # instant hoặc scheduled
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    settings: Optional[RoomSettings] = None

@router.post("/create")
async def create_room(
    req: CreateRoomRequest,
    current_user: dict = Depends(get_current_user)
):
    """Tạo meeting room mới"""
    email = current_user["sub"]
    name = current_user.get("name") or email
    
    room = await meeting_service.create_room(
        room_type=req.room_type,
        host_email=email,
        host_name=name,
        title=req.title,
        description=req.description,
        scheduled_at=req.scheduled_at,
        settings=req.settings
    )
    
    return {
        "room_id": room.room_id,
        "room_type": room.room_type,
        "title": room.title,
        "status": room.status,
        "join_url": f"/meeting/{room.room_id}",
        "ws_url": f"/ws/meeting/{room.room_id}"
    }

@router.get("/{room_id}")
async def get_room_info(
    room_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lấy thông tin room trước khi join"""
    email = current_user["sub"]
    can_join, error, room = await meeting_service.can_join(room_id, email)
    
    return {
        "room": room.model_dump() if room else None,
        "can_join": can_join,
        "error": error,
        "is_host": room.host_email == email if room else False
    }

@router.post("/{room_id}/end")
async def end_room(
    room_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Host kết thúc room"""
    email = current_user["sub"]
    success = await meeting_service.end_room(room_id, email)
    if not success:
        raise HTTPException(status_code=403, detail="Không có quyền hoặc room không tồn tại")
    return {"status": "ended"}

# Upload file cho meeting chat (dùng FileService sẵn có)
@router.post("/upload")
async def upload_meeting_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload file cho chat trong meeting"""
    try:
        file_id = await FileService.upload_file(file)
        url = FileService.get_file_url(file_id)
        return {
            "file_id": file_id,
            "url": url,
            "filename": file.filename,
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))