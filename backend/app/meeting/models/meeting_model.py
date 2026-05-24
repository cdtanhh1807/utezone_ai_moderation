from datetime import datetime as dt
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class Participant(BaseModel):
    email: str
    username: str
    socket_id: Optional[str] = None
    joined_at: dt = Field(default_factory=dt.now)
    is_host: bool = False
    audio_on: bool = True
    video_on: bool = True

class RoomSettings(BaseModel):
    require_approval: bool = False
    allow_chat_files: bool = True
    mute_on_entry: bool = False
    video_on_entry: bool = True

class MeetingRoom(BaseModel):
    room_id: str
    room_type: Literal["instant", "scheduled"] = "instant"
    host_email: str
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[dt] = None
    started_at: Optional[dt] = None
    ended_at: Optional[dt] = None
    expires_at: Optional[dt] = None
    participants: List[Participant] = []
    settings: RoomSettings = Field(default_factory=RoomSettings)
    status: Literal["waiting", "active", "ended"] = "waiting"
    whiteboard_data: Optional[str] = None
    created_at: dt = Field(default_factory=dt.now)

class MeetingMessage(BaseModel):
    room_id: str
    sender_email: str
    sender_name: str
    message_type: Literal["text", "file", "image", "video", "system"] = "text"
    content: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    created_at: dt = Field(default_factory=dt.now)
    
    class Config:
        json_encoders = {dt: lambda v: v.isoformat()}