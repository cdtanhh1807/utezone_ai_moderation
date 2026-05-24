from motor.motor_asyncio import AsyncIOMotorCollection
from core.database import db
from dto.message.response.conversation_response import ConversationResponse
from models.message_model import Message
from datetime import datetime, timezone
from typing import List
from models.base_model import bson_to_dict
import pytz

from repositories.account_repository import AccountRepository
from repositories.conversation_repository import ConversationRepository


class MessageRepository:
    collection = db["message"]

    @staticmethod
    async def insert_message(msg: Message) -> Message:
        doc = msg.model_dump(by_alias=True, exclude={"id"})
        result = await MessageRepository.collection.insert_one(doc)
        msg.id = result.inserted_id
        return msg

    @staticmethod
    async def get_conversation(
        conversation_id: str, skip: int = 0, limit: int = 50
    ) -> List[Message]:
        cursor = (
            MessageRepository.collection.find({"conversation_id": conversation_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [Message(**bson_to_dict(d)) for d in docs]

    @staticmethod
    async def get_all(email: str) -> List[ConversationResponse]:
    # 1.  lastSeen cho mỗi cuộc (nếu chưa -> mặc định EPOCH)
        pipeline_last_seen = [
            {"$match": {"user": email}},
            {"$group": {"_id": "$other", "time": {"$max": "$time"}}}
        ]
        seen_cursor = db["conversation_last_seen"].aggregate(pipeline_last_seen)
        seen_map = {doc["_id"]: doc["time"] async for doc in seen_cursor}

        # 2.  cuộc trò chuyện + tin mới nhất
        pipeline_conv = [
            {"$match": {
                "$or": [{"sender_email": email}, {"receiver_email": email}],
                "$expr": {"$ne": ["$sender_email", "$receiver_email"]}  # loại tự nhắn
            }},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": {"$cond": [{"$eq": ["$sender_email", email]}, "$receiver_email", "$sender_email"]},
                "last_message": {"$first": "$content"},
                "last_time": {"$first": "$created_at"},
            }},
            {"$sort": {"last_time": -1}},
            {"$limit": 50},
        ]
        conv_cursor = db["message"].aggregate(pipeline_conv)
        docs = await conv_cursor.to_list(length=50)

        # 3.  đếm unread & build response
        res = []
        for d in docs:
            other = d["_id"]
            last_time = d["last_time"]
            seen_time = seen_map.get(other, datetime(1970, 1, 1, tzinfo=pytz.UTC))

            unread = await db["message"].count_documents({
                "conversation_id": "_".join(sorted([email, other])),
                "sender_email": other,  # chỉ tin NGƯỜI KHÁC gửi
                "created_at": {"$gt": seen_time}
            })

            res.append(ConversationResponse(
                other_email=other,
                last_message=d["last_message"],
                last_time=last_time,
                unread=unread
            ))
        return res
    
    @staticmethod
    async def get_conversations_with_unread(user: str) -> List[dict]:
        """
        Trả về [{other_email, last_message, last_time, has_new}]
        """
        # 1. danh sách cuộc + tin cuối
        pipeline = [
            {"$match": {
                "$or": [{"sender_email": user}, {"receiver_email": user}],
                "$expr": {"$ne": ["$sender_email", "$receiver_email"]}
            }},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": {"$cond": [{"$eq": ["$sender_email", user]}, "$receiver_email", "$sender_email"]},
                "last_message": {"$first": "$content"},
                "last_time":   {"$first": "$created_at"},
            }},
            {"$sort": {"last_time": -1}},
            {"$limit": 50}
        ]
        docs = await MessageRepository.collection.aggregate(pipeline).to_list(length=50)

        # 2. tính has_new cho mỗi cuộc
        res = []
        for d in docs:
            other      = d["_id"]
            last_time  = d["last_time"]

            # lấy fullName
            acc = await AccountRepository.find_by_email(other)
            full_name = acc["userInfo"]["fullName"] if acc and acc["userInfo"] else other

            seen_time = await ConversationRepository.get_last_seen(user, other) or datetime(1970, 1, 1, tzinfo=pytz.UTC)
            has_new   = await MessageRepository.collection.count_documents({
                "conversation_id": "_".join(sorted([user, other])),
                "sender_email": other,
                "created_at": {"$gt": seen_time}
            }) > 0

            res.append({
                "other_email": other,
                "full_name": full_name,
                "last_message": d["last_message"],
                "last_time": last_time,
                "has_new": has_new
            })
        return res