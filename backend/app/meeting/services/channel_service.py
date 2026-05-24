from datetime import datetime as dt, timedelta
from typing import Optional, List, Dict
import uuid
from core.database import db
from meeting.models.channel_model import Channel, ChannelRules, ChatRoom, ChannelMember, UserSession, Message
from meeting.services.meeting_service import meeting_service


class ChannelService:
    def __init__(self):
        self.db = db
        self.channels_col = db.channels
        self.chatrooms_col = db.chat_rooms
        self.sessions_col = db.user_sessions
        self.messages_col = db.messages

    # ==================== CHANNEL CRUD ====================

    async def create_channel(self, owner_email: str, owner_name: str,
                              name: str, description: Optional[str] = None,
                              require_approval: bool = False) -> Channel:
        # existing = await self.channels_col.find_one({"owner_email": owner_email})
        # if existing:
        #     raise ValueError("Mỗi tài khoản chỉ có thể tạo 1 channel")

        channel = Channel(
            owner_email=owner_email,
            name=name,
            description=description,
            require_approval=require_approval,
            members=[ChannelMember(
                email=owner_email,
                username=owner_name,
                role="owner",
                status="approved"
            )]
        )

        await self.channels_col.insert_one(channel.model_dump())

        general_room = ChatRoom(
            channel_id=channel.channel_id,
            name="Phòng chung",
            description="Phòng trò chuyện chung",
            room_type="text",
            created_by=owner_email
        )
        await self.chatrooms_col.insert_one(general_room.model_dump())

        return channel

    async def get_channel(self, channel_id: str) -> Optional[Channel]:
        data = await self.channels_col.find_one({"channel_id": channel_id})
        if data:
            data.pop("_id", None)
            return Channel(**data)
        return None

    async def get_channel_by_owner(self, owner_email: str) -> Optional[Channel]:
        data = await self.channels_col.find_one({"owner_email": owner_email})
        if data:
            data.pop("_id", None)
            return Channel(**data)
        return None

    async def get_channel_by_invite_code(self, invite_code: str) -> Optional[Channel]:
        data = await self.channels_col.find_one({"invite_code": invite_code})
        if data:
            data.pop("_id", None)
            return Channel(**data)
        return None

    async def update_channel(self, channel_id: str, owner_email: str, **kwargs) -> Optional[Channel]:
        channel = await self.get_channel(channel_id)
        if not channel:
            raise ValueError("Channel không tồn tại")
        if channel.owner_email != owner_email:
            raise ValueError("Chỉ chủ channel mới có thể cập nhật")

        update_data = {}
        for key, value in kwargs.items():
            if value is not None or key == 'avatar':
                update_data[key] = value

        if update_data:
            update_data["updated_at"] = dt.now()
            await self.channels_col.update_one(
                {"channel_id": channel_id},
                {"$set": update_data}
            )

        return await self.get_channel(channel_id)

    async def delete_channel(self, channel_id: str, owner_email: str) -> bool:
        channel = await self.get_channel(channel_id)
        if not channel or channel.owner_email != owner_email:
            return False

        chatrooms = await self.chatrooms_col.find({"channel_id": channel_id}).to_list(length=1000)
        for cr in chatrooms:
            if cr.get("meeting_room_id"):
                try:
                    await meeting_service.end_room(cr["meeting_room_id"], owner_email)
                except:
                    pass

        await self.chatrooms_col.delete_many({"channel_id": channel_id})
        await self.messages_col.delete_many({"channel_id": channel_id})
        await self.channels_col.delete_one({"channel_id": channel_id})
        await self.sessions_col.delete_many({"current_channel_id": channel_id})

        return True

    async def get_my_channels(self, email: str) -> List[dict]:
        channels = []
        cursor = self.channels_col.find({
            "members": {"$elemMatch": {"email": email, "status": "approved"}}
        })
        async for data in cursor:
            data.pop("_id", None)
            channels.append(data)
        return channels

    # ==================== CHANNEL MEMBERSHIP ====================

    async def join_channel(self, email: str, username: str,
                           invite_code: Optional[str] = None,
                           channel_id: Optional[str] = None) -> dict:
        channel = None
        if invite_code:
            channel = await self.get_channel_by_invite_code(invite_code)
        elif channel_id:
            channel = await self.get_channel(channel_id)

        if not channel:
            return {"success": False, "error": "Channel không tồn tại"}

        for m in channel.members:
            if m.email == email:
                if m.status == "approved":
                    return {"success": True, "channel_id": channel.channel_id, "message": "Đã là thành viên"}
                elif m.status == "pending":
                    return {"success": False, "error": "Đang chờ phê duyệt"}
                elif m.status == "rejected":
                    break

        new_member = ChannelMember(
            email=email,
            username=username,
            role="member",
            status="pending" if channel.require_approval else "approved"
        )

        await self.channels_col.update_one(
            {"channel_id": channel.channel_id},
            {"$pull": {"members": {"email": email}}}
        )

        await self.channels_col.update_one(
            {"channel_id": channel.channel_id},
            {"$push": {"members": new_member.model_dump()}}
        )

        if channel.require_approval:
            return {"success": True, "channel_id": channel.channel_id, "status": "pending", "message": "Đã gửi yêu cầu tham gia, chờ phê duyệt"}
        else:
            return {"success": True, "channel_id": channel.channel_id, "status": "approved", "message": "Tham gia channel thành công"}

    async def leave_channel(self, email: str, channel_id: str) -> dict:
        channel = await self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel không tồn tại"}

        if channel.owner_email == email:
            return {"success": False, "error": "Chủ channel không thể rời channel. Hãy xóa channel nếu muốn."}

        await self.channels_col.update_one(
            {"channel_id": channel_id},
            {"$pull": {"members": {"email": email}}}
        )

        await self.clear_user_session(email)

        return {"success": True, "message": "Đã rời channel"}

    async def approve_member(self, channel_id: str, owner_email: str,
                              member_email: str, approve: bool) -> dict:
        channel = await self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel không tồn tại"}
        if channel.owner_email != owner_email:
            return {"success": False, "error": "Chỉ chủ channel mới có thể phê duyệt"}

        new_status = "approved" if approve else "rejected"
        await self.channels_col.update_one(
            {"channel_id": channel_id, "members.email": member_email},
            {"$set": {"members.$.status": new_status}}
        )

        if not approve:
            await self.channels_col.update_one(
                {"channel_id": channel_id},
                {"$pull": {"members": {"email": member_email}}}
            )

        return {"success": True, "member_email": member_email, "status": new_status}

    async def get_pending_members(self, channel_id: str, owner_email: str) -> List[dict]:
        channel = await self.get_channel(channel_id)
        if not channel or channel.owner_email != owner_email:
            return []

        pending = [m.model_dump() for m in channel.members if m.status == "pending"]
        return pending

    async def kick_member(self, channel_id: str, owner_email: str, member_email: str) -> dict:
        channel = await self.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": "Channel không tồn tại"}
        if channel.owner_email != owner_email:
            return {"success": False, "error": "Chỉ chủ channel mới có thể kick"}
        if channel.owner_email == member_email:
            return {"success": False, "error": "Không thể kick chủ channel"}

        await self.channels_col.update_one(
            {"channel_id": channel_id},
            {"$pull": {"members": {"email": member_email}}}
        )

        return {"success": True, "message": f"Đã kick {member_email}"}

    # ==================== CHAT ROOM CRUD ====================

    async def create_chat_room(self, channel_id: str, owner_email: str,
                                name: str, description: Optional[str] = None,
                                room_type: str = "text") -> ChatRoom:
        channel = await self.get_channel(channel_id)
        if not channel:
            raise ValueError("Channel không tồn tại")
        if channel.owner_email != owner_email:
            raise ValueError("Chỉ chủ channel mới có thể tạo chat room")

        chatroom = ChatRoom(
            channel_id=channel_id,
            name=name,
            description=description,
            room_type=room_type,
            created_by=owner_email
        )

        await self.chatrooms_col.insert_one(chatroom.model_dump())
        return chatroom

    async def get_chat_room(self, room_id: str) -> Optional[ChatRoom]:
        data = await self.chatrooms_col.find_one({"room_id": room_id})
        if data:
            data.pop("_id", None)
            return ChatRoom(**data)
        return None

    async def get_channel_chat_rooms(self, channel_id: str) -> List[dict]:
        chatrooms = []
        cursor = self.chatrooms_col.find({"channel_id": channel_id}).sort("created_at", 1)
        async for data in cursor:
            data.pop("_id", None)
            chatrooms.append(data)
        return chatrooms

    async def update_chat_room(self, room_id: str, owner_email: str, **kwargs) -> Optional[ChatRoom]:
        chatroom = await self.get_chat_room(room_id)
        if not chatroom:
            raise ValueError("Chat room không tồn tại")

        channel = await self.get_channel(chatroom.channel_id)
        if not channel or channel.owner_email != owner_email:
            raise ValueError("Chỉ chủ channel mới có thể cập nhật chat room")

        update_data = {}
        for key, value in kwargs.items():
            if value is not None:
                update_data[key] = value

        if update_data:
            update_data["updated_at"] = dt.now()
            await self.chatrooms_col.update_one(
                {"room_id": room_id},
                {"$set": update_data}
            )

        return await self.get_chat_room(room_id)

    async def delete_chat_room(self, room_id: str, owner_email: str) -> bool:
        chatroom = await self.get_chat_room(room_id)
        if not chatroom:
            return False

        channel = await self.get_channel(chatroom.channel_id)
        if not channel or channel.owner_email != owner_email:
            return False

        if chatroom.meeting_room_id:
            try:
                await meeting_service.end_room(chatroom.meeting_room_id, owner_email)
            except:
                pass

        await self.chatrooms_col.delete_one({"room_id": room_id})
        await self.messages_col.delete_many({"room_id": room_id})
        await self.sessions_col.delete_many({"current_chat_room_id": room_id})

        return True

    async def start_meeting_in_chatroom(self, room_id: str, owner_email: str,
                                         host_name: str) -> dict:
        chatroom = await self.get_chat_room(room_id)
        if not chatroom:
            raise ValueError("Chat room không tồn tại")

        channel = await self.get_channel(chatroom.channel_id)
        if not channel:
            raise ValueError("Channel không tồn tại")

        is_member = any(m.email == owner_email and m.status == "approved" for m in channel.members)
        if not is_member:
            raise ValueError("Bạn không phải thành viên của channel này")

        if chatroom.meeting_room_id:
            meeting_room = await meeting_service.get_room(chatroom.meeting_room_id)
            if meeting_room and meeting_room.status != "ended":
                return {
                    "meeting_room_id": chatroom.meeting_room_id,
                    "room_id": chatroom.meeting_room_id,
                    "status": meeting_room.status
                }

        meeting_room = await meeting_service.create_room(
            room_type="instant",
            host_email=owner_email,
            host_name=host_name,
            title=f"{chatroom.name} - Meeting"
        )

        await self.chatrooms_col.update_one(
            {"room_id": room_id},
            {"$set": {"meeting_room_id": meeting_room.room_id}}
        )

        return {
            "meeting_room_id": meeting_room.room_id,
            "room_id": meeting_room.room_id,
            "status": "active"
        }

    # ==================== USER SESSION ====================

    async def set_user_session(self, email: str, channel_id: Optional[str],
                                chat_room_id: Optional[str]) -> dict:
        if channel_id:
            channel = await self.get_channel(channel_id)
            if not channel:
                raise ValueError("Channel không tồn tại")
            is_member = any(m.email == email and m.status == "approved" for m in channel.members)
            if not is_member:
                raise ValueError("Bạn không phải thành viên của channel này")

        if chat_room_id:
            chatroom = await self.get_chat_room(chat_room_id)
            if not chatroom:
                raise ValueError("Chat room không tồn tại")
            if chatroom.channel_id != channel_id:
                raise ValueError("Chat room không thuộc channel này")

        session = UserSession(
            email=email,
            current_channel_id=channel_id,
            current_chat_room_id=chat_room_id
        )

        await self.sessions_col.update_one(
            {"email": email},
            {"$set": session.model_dump()},
            upsert=True
        )

        return {"success": True, "channel_id": channel_id, "chat_room_id": chat_room_id}

    async def get_user_session(self, email: str) -> Optional[dict]:
        data = await self.sessions_col.find_one({"email": email})
        if data:
            data.pop("_id", None)
            return data
        return None

    async def clear_user_session(self, email: str) -> bool:
        result = await self.sessions_col.delete_one({"email": email})
        return result.deleted_count > 0

    async def get_online_users_in_channel(self, channel_id: str) -> List[dict]:
        sessions = []
        cursor = self.sessions_col.find({"current_channel_id": channel_id})
        async for data in cursor:
            data.pop("_id", None)
            sessions.append(data)
        return sessions

    async def get_online_users_in_chatroom(self, chat_room_id: str) -> List[dict]:
        sessions = []
        cursor = self.sessions_col.find({"current_chat_room_id": chat_room_id})
        async for data in cursor:
            data.pop("_id", None)
            sessions.append(data)
        return sessions


    # ==================== MESSAGES ====================

    async def send_message(self, room_id: str, channel_id: str,
                        sender_email: str, sender_name: str,
                        content: str, msg_type: str = "text", file_name: str = None) -> Message:
        chatroom = await self.get_chat_room(room_id)
        if not chatroom:
            raise ValueError("Chat room không tồn tại")
        if chatroom.room_type == "voice":
            raise ValueError("Không thể gửi tin nhắn trong phòng voice")
        channel = await self.get_channel(channel_id)
        if not channel:
            raise ValueError("Channel không tồn tại")
        is_member = any(m.email == sender_email and m.status == "approved" for m in channel.members)
        if not is_member:
            raise ValueError("Bạn không phải thành viên của channel này")

        message = Message(
            room_id=room_id,
            channel_id=channel_id,
            sender_email=sender_email,
            sender_name=sender_name,
            content=content,
            msg_type=msg_type,      # lưu loại tin nhắn
            file_name=file_name     # lưu tên file nếu có
        )
        await self.messages_col.insert_one(message.model_dump())
        return message

    async def get_messages(self, room_id: str, limit: int = 50, before: Optional[str] = None) -> List[dict]:
        query = {"room_id": room_id}
        if before:
            query["message_id"] = {"$lt": before}
        messages = []
        cursor = self.messages_col.find(query).sort("created_at", 1).limit(limit)
        async for data in cursor:
            data.pop("_id", None)
            messages.append(data)
        return messages
    
    async def delete_message(self, message_id: str, channel_id: str) -> bool:
        result = await self.messages_col.delete_one({
            "message_id": message_id,
            "channel_id": channel_id
        })
        return result.deleted_count > 0

    async def update_read_status(self, email: str, room_id: str, message_id: str = None):
        """Cập nhật thời gian đọc cuối cùng của user trong room"""
        await self.db.user_read_status.update_one(
            {"email": email, "room_id": room_id},
            {"$set": {
                "last_read_at": dt.now(),
                "last_read_message_id": message_id
            }},
            upsert=True
        )

    async def get_unread_count(self, email: str, room_id: str) -> int:
        """Lấy số tin nhắn chưa đọc trong room"""
        status = await self.db.user_read_status.find_one(
            {"email": email, "room_id": room_id}
        )
        last_read = status["last_read_at"] if status else dt.now() - timedelta(days=365)
        # Đếm tin nhắn trong room có created_at > last_read
        count = await self.db.messages.count_documents({
            "room_id": room_id,
            "created_at": {"$gt": last_read}
        })
        return count

    async def get_unread_counts_for_channel(self, email: str, channel_id: str) -> dict:
        """Lấy unread count cho tất cả room trong channel"""
        rooms = await self.get_channel_chat_rooms(channel_id)
        result = {}
        for room in rooms:
            room_id = room["room_id"]
            result[room_id] = await self.get_unread_count(email, room_id)
        return result

    async def get_last_message(self, room_id: str):
        """Lấy tin nhắn mới nhất trong room"""
        data = await self.messages_col.find_one(
            {"room_id": room_id},
            sort=[("created_at", -1)]
        )
        if data:
            return Message(**data)
        return None
    
    async def search_messages(self, room_id: str, keyword: str, limit: int = 50) -> List[dict]:
        """Tìm kiếm tin nhắn trong room (case-insensitive)"""
        query = {
            "room_id": room_id,
            "content": {"$regex": keyword, "$options": "i"}
        }
        cursor = self.messages_col.find(query).sort("created_at", -1).limit(limit)
        messages = []
        async for doc in cursor:
            doc.pop("_id", None)
            messages.append(doc)
        return messages
    
    # ==================== AI MODERATION ====================
    async def get_channel_rules(self, channel_id: str) -> Optional['ChannelRules']:
        data = await self.db.channel_rules.find_one({"channel_id": channel_id})
        if not data:
            return None
        from meeting.models.channel_model import ChannelRules
        return ChannelRules(**data)

    async def save_channel_rules(self, rules: 'ChannelRules'):
        await self.db.channel_rules.update_one(
            {"channel_id": rules.channel_id},
            {"$set": rules.model_dump()},
            upsert=True
        )

    async def add_violation(self, email: str, channel_id: str, rule_type: str) -> int:
        from datetime import datetime, timedelta
        one_day_ago = datetime.now() - timedelta(days=1)
        count = await self.db.violations_meet.count_documents({
            "email": email,
            "channel_id": channel_id,
            "rule_type": rule_type,
            "created_at": {"$gt": one_day_ago}
        })
        await self.db.violations_meet.insert_one({
            "email": email,
            "channel_id": channel_id,
            "rule_type": rule_type,
            "created_at": datetime.now()
        })
        return count + 1

    async def mute_user(self, email: str, channel_id: str, minutes: int):
        from datetime import datetime, timedelta
        expire_at = datetime.now() + timedelta(minutes=minutes)
        await self.db.muted_users.update_one(
            {"email": email, "channel_id": channel_id},
            {"$set": {"expire_at": expire_at}},
            upsert=True
        )
        # Tạo TTL index (chạy một lần khi khởi tạo)
        await self.db.muted_users.create_index("expire_at", expireAfterSeconds=0)

    async def is_muted(self, email: str, channel_id: str) -> bool:
        from datetime import datetime
        muted = await self.db.muted_users.find_one({
            "email": email,
            "channel_id": channel_id,
            "expire_at": {"$gt": datetime.now()}
        })
        return muted is not None

channel_service = ChannelService()
