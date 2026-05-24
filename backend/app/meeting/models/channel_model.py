from datetime import datetime as dt
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
import uuid


class ChannelMember(BaseModel):
    email: str
    username: Optional[str] = None
    role: Literal["owner", "member"] = "member"
    status: Literal["pending", "approved", "rejected"] = "approved"
    joined_at: dt = Field(default_factory=dt.now)


class Channel(BaseModel):
    channel_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    owner_email: str
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    invite_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    require_approval: bool = False
    members: List[ChannelMember] = []
    created_at: dt = Field(default_factory=dt.now)
    updated_at: Optional[dt] = None


class ChatRoom(BaseModel):
    room_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:10])
    channel_id: str
    name: str
    description: Optional[str] = None
    room_type: Literal["text", "voice"] = "text"
    meeting_room_id: Optional[str] = None
    created_by: str
    created_at: dt = Field(default_factory=dt.now)
    updated_at: Optional[dt] = None


class UserSession(BaseModel):
    email: str
    current_channel_id: Optional[str] = None
    current_chat_room_id: Optional[str] = None
    last_active: dt = Field(default_factory=dt.now)


class CreateChannelRequest(BaseModel):
    name: str
    description: Optional[str] = None
    require_approval: bool = False


class UpdateChannelRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    require_approval: Optional[bool] = None


class CreateChatRoomRequest(BaseModel):
    name: str
    description: Optional[str] = None
    room_type: Literal["text", "voice"] = "text"


class UpdateChatRoomRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class JoinChannelRequest(BaseModel):
    invite_code: Optional[str] = None


class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    room_id: str
    channel_id: str
    sender_email: str
    sender_name: Optional[str] = None
    content: str
    msg_type: Literal["text", "image", "video", "file"] = "text"
    file_name: Optional[str] = None
    created_at: dt = Field(default_factory=dt.now)


class SendMessageRequest(BaseModel):
    content: str
    msg_type: Optional[str] = "text"
    file_id: Optional[str] = None
    file_name: Optional[str] = None


class ApproveMemberRequest(BaseModel):
    email: str
    approve: bool

class UserReadStatus(BaseModel):
    email: str
    room_id: str
    last_read_at: dt = Field(default_factory=dt.now)
    last_read_message_id: Optional[str] = None

#AI
class RuleItem(BaseModel):
    type: Literal["text", "image", "video", "file", "all"] = "text"
    action: Literal["warn", "mute", "kick", "ban"] = "warn"
    max_violations: int = 3
    penalty_time: Optional[int] = None  # minutes for mute

class ChannelRules(BaseModel):
    channel_id: str
    enabled: bool = False
    rules_text: str = ""  # nội dung luật (tự nhiên)
    enabled_types: List[Literal["text","image","video","file"]] = []
    action: Literal["warn","mute","kick","ban"] = "warn"
    max_violations: int = 3
    penalty_time: Optional[int] = None
    updated_at: dt = Field(default_factory=dt.now)
    updated_by: str