from datetime import datetime as dt, timedelta
from typing import Optional, List, Dict
import uuid
from core.database import db
from meeting.models.meeting_model import MeetingRoom, Participant, RoomSettings
from services.other.file_service import FileService 

class MeetingService:
    def __init__(self):
        self.db = db
        self.collection = db.meeting_rooms
        
    async def create_room(self, room_type: str, host_email: str, 
                         host_name: str, title: Optional[str] = None,
                         description: Optional[str] = None,
                         scheduled_at: Optional[dt] = None,
                         settings: Optional[RoomSettings] = None) -> MeetingRoom:
        if room_type == "instant":
            room_id = str(uuid.uuid4())[:8]
            status = "active"
            started_at = dt.now()
            expires_at = dt.now() + timedelta(hours=24)
        else:
            room_id = str(uuid.uuid4())
            status = "waiting"
            started_at = None
            expires_at = None
            
        room = MeetingRoom(
            room_id=room_id,
            room_type=room_type,
            host_email=host_email,
            title=title or ("Cuộc họp nhanh" if room_type == "instant" else "Cuộc họp đã lên lịch"),
            description=description,
            scheduled_at=scheduled_at,
            started_at=started_at,
            ended_at=None,
            expires_at=expires_at,
            status=status,
            settings=settings or RoomSettings(),
            participants=[Participant(email=host_email, username=host_name, is_host=True)]
        )
        
        await self.collection.insert_one(room.model_dump())
        return room
    
    async def get_room(self, room_id: str) -> Optional[MeetingRoom]:
        data = await self.collection.find_one({"room_id": room_id})
        return MeetingRoom(**data) if data else None
    
    async def can_join(self, room_id: str, user_email: str) -> tuple[bool, Optional[str], Optional[MeetingRoom]]:
        room = await self.get_room(room_id)
        if not room:
            return False, "Room không tồn tại", None
            
        if room.status == "ended":
            return False, "Cuộc họp đã kết thúc", None
            
        if room.room_type == "scheduled" and room.status == "waiting":
            if room.host_email != user_email:
                return False, "Cuộc họp chưa bắt đầu, chờ host mở", room
            await self.start_room(room_id)
            room.status = "active"
            room.started_at = dt.now()
            
        if room.scheduled_at and room.scheduled_at > dt.now() + timedelta(minutes=5):
            if room.host_email != user_email:
                return False, "Chưa đến giờ họp", room
                
        existing = any(p.email == user_email for p in room.participants)
        if existing:
            return True, None, room
            
        if room.settings.require_approval and room.host_email != user_email:
            return False, "Đang chờ host phê duyệt", room
            
        return True, None, room
    
    async def add_participant(self, room_id: str, email: str, username: str, socket_id: str):
        await self.collection.update_one(
            {"room_id": room_id},
            {"$addToSet": {"participants": {
                "email": email,
                "username": username,
                "socket_id": socket_id,
                "joined_at": dt.now(),
                "is_host": False,
                "audio_on": True,
                "video_on": True
            }}}
        )
        await self.collection.update_one(
            {"room_id": room_id, "status": "waiting"},
            {"$set": {"status": "active", "started_at": dt.now()}}
        )
    
    async def remove_participant(self, room_id: str, socket_id: str) -> bool:
        await self.collection.update_one(
            {"room_id": room_id},
            {"$pull": {"participants": {"socket_id": socket_id}}}
        )
        room = await self.get_room(room_id)
        if room and len(room.participants) == 0 and room.room_type == "instant":
            await self.end_room(room_id, room.host_email)
            return True
        return False
    
    async def update_socket_id(self, room_id: str, email: str, socket_id: str):
        await self.collection.update_one(
            {"room_id": room_id, "participants.email": email},
            {"$set": {"participants.$.socket_id": socket_id}}
        )
    
    async def update_media_status(self, room_id: str, socket_id: str, 
                                  audio: Optional[bool] = None, 
                                  video: Optional[bool] = None):
        update_data = {}
        if audio is not None:
            update_data["participants.$.audio_on"] = audio
        if video is not None:
            update_data["participants.$.video_on"] = video
            
        if update_data:
            await self.collection.update_one(
                {"room_id": room_id, "participants.socket_id": socket_id},
                {"$set": update_data}
            )
    
    async def start_room(self, room_id: str):
        await self.collection.update_one(
            {"room_id": room_id},
            {"$set": {"status": "active", "started_at": dt.now()}}
        )
    
    async def save_message(self, room_id: str, sender_email: str, sender_name: str,
                           message_type: str, content: str, 
                           file_name: Optional[str] = None,
                           file_size: Optional[int] = None) -> dict:
        message = {
            "room_id": room_id,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "message_type": message_type,
            "content": content,
            "file_name": file_name,
            "file_size": file_size,
            "created_at": dt.now()
        }
        
        result = await self.db.meeting_messages.insert_one(message)
        message["_id"] = str(result.inserted_id)
        
        if message_type in ["file", "image", "video"]:
            message["file_url"] = FileService.get_file_url(content)
        
        return message
    
    async def get_messages(self, room_id: str, limit: int = 100) -> List[dict]:
        cursor = self.db.meeting_messages.find(
            {"room_id": room_id}
        ).sort("created_at", -1).limit(limit)
        
        messages = await cursor.to_list(length=limit)
        messages.reverse()
        
        for msg in messages:
            msg["_id"] = str(msg["_id"])
            if msg.get("message_type") in ["file", "image", "video"]:
                msg["file_url"] = FileService.get_file_url(msg["content"])
        
        return messages
    
    async def delete_room_files(self, room_id: str) -> int:
        messages = await self.db.meeting_messages.find({
            "room_id": room_id,
            "message_type": {"$in": ["file", "image", "video"]}
        }).to_list(length=1000)
        
        deleted = 0
        from core.minio import minio_client, MINIO_BUCKET
        
        for msg in messages:
            file_id = msg.get("content")
            if file_id:
                try:
                    minio_client.remove_object(MINIO_BUCKET, file_id)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to delete {file_id}: {e}")
        
        return deleted
    
    async def delete_room_messages(self, room_id: str):
        await self.db.meeting_messages.delete_many({"room_id": room_id})
    
    async def end_room(self, room_id: str, host_email: str) -> dict:
        room = await self.get_room(room_id)
        if not room or room.host_email != host_email:
            return {"success": False, "error": "Unauthorized or room not found"}
        
        await self.collection.update_one(
            {"room_id": room_id},
            {"$set": {"status": "ended", "ended_at": dt.now()}}
        )
        
        deleted_files = await self.delete_room_files(room_id)
        await self.delete_room_messages(room_id)
        
        return {
            "success": True,
            "room_id": room_id,
            "deleted_files": deleted_files,
            "ended_at": dt.now().isoformat()
        }
    
    async def save_whiteboard(self, room_id: str, canvas_data: str):
        await self.collection.update_one(
            {"room_id": room_id},
            {"$set": {"whiteboard_data": canvas_data}}
        )
    
    async def get_whiteboard(self, room_id: str) -> Optional[str]:
        room = await self.get_room(room_id)
        return room.whiteboard_data if room else None

meeting_service = MeetingService()