from datetime import datetime, timezone
from typing import Optional
from core.database import db
from dto.message.response.conversation_response import ConversationResponse

class ConversationRepository:
    
    collection = db["conversation"]

    @staticmethod
    async def update_last_seen(user: str, other: str, when: datetime) -> None:
        """Cập nhật thời điểm `user` đã xem cuộc trò chuyện với `other`."""
        cid = "_".join(sorted([user, other]))
        safe_user = user.replace('.', '_')  
        await ConversationRepository.collection.update_one(
            {"_id": cid},
            {"$set": {f"last_seen.{safe_user}": when}},
            upsert=True
        )

    @staticmethod
    async def get_last_seen(user: str, other: str) -> Optional[datetime]:
        cid = "_".join(sorted([user, other]))
        doc = await ConversationRepository.collection.find_one(
            {"_id": cid},
            {f"last_seen.{user.replace('.', '_')}": 1}  # <- dùng key giống lúc ghi
        )
        if not doc or "last_seen" not in doc:
            return None
        ts = doc["last_seen"].get(user.replace('.', '_'))  # <- đọc cùng key
        return ts
    
    @staticmethod
    async def get_conversation_response(user_email: str, other_email: str) -> ConversationResponse | None:

        conversation_id = "_".join(sorted([user_email, other_email]))

        # Lấy tin nhắn mới nhất
        last_msg = await db["message"].find_one(
            {"conversation_id": conversation_id},
            sort=[("created_at", -1)]
        )
        if not last_msg:
            return None

        # Lấy last_seen
        conv = await db.conversation.find_one({"_id": conversation_id})
        last_seen = None
        if conv and "last_seen" in conv:
            key = user_email.replace(".", "_")
            last_seen = conv["last_seen"].get(key)

        has_new = last_seen is None or last_msg["created_at"] > last_seen

        # Lấy full_name
        acc = await ConversationRepository.collection.find_one({"email": other_email})
        full_name = acc["userInfo"]["fullName"] if acc and acc.get("userInfo") else other_email

        return ConversationResponse(
            other_email=other_email,
            full_name=full_name,
            last_message=last_msg["content"],
            last_time=last_msg["created_at"],
            has_new=has_new
        )