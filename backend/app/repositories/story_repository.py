from bson import ObjectId
from core.database import db
from datetime import datetime, timedelta, timezone
from repositories.account_repository import AccountRepository
from utils.base import bson_to_dict

class StoryRepository:
    collection = db["story"]

    @staticmethod
    async def add_story(story_data: dict) -> dict:
        result = await StoryRepository.collection.insert_one(story_data)
        inserted_story = await StoryRepository.collection.find_one({"_id": result.inserted_id})
        return bson_to_dict(inserted_story)

    @staticmethod
    async def find_by_user(user_id: str) -> list[dict]:
        cursor = StoryRepository.collection.find({
            "createdBy": user_id,
            "status": "active",
            "expiresAt": {"$gt": datetime.now(timezone.utc)}
        })
        stories = await cursor.to_list(length=None)
        return [bson_to_dict(story) for story in stories]

    @staticmethod
    async def find_all_active() -> list[dict]:
        cursor = StoryRepository.collection.find({
            "status": "active",
            "expiresAt": {"$gt": datetime.now(timezone.utc)}
        })
        stories = await cursor.to_list(length=None)
        return [bson_to_dict(story) for story in stories]

    @staticmethod
    async def find_today_stories(myAccount: dict) -> list[dict]:
        """Lấy story trong 24h và active, lọc mutual block, ưu tiên stories từ người bạn follow"""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)

        my_email = myAccount.get("email")
        my_blocks = myAccount["userInfo"].get("blocks", [])
        followed_list = set(myAccount["userInfo"].get("followed", []))

        # 1. Query sơ bộ: active, trong 24h, chưa hết hạn, loại bỏ stories của account bạn block
        cursor = StoryRepository.collection.find({
            "status": "active",
            "createdAt": {"$gte": last_24h},
            "expiresAt": {"$gt": now},
            "createdBy": {"$nin": my_blocks}
        })

        stories = await cursor.to_list(length=None)

        # 2. Mutual block filter + đánh dấu followed
        filtered_stories = []
        for story in stories:
            author_email = story.get("createdBy")
            author = await AccountRepository.collection.find_one({"email": author_email})
            if not author:
                continue
            # Loại nếu author đã block bạn
            if my_email in author["userInfo"].get("blocks", []):
                continue
            # Thêm flag ưu tiên followed
            story_dict = bson_to_dict(story)
            story_dict["_isFollowed"] = 1 if author_email in followed_list else 0
            filtered_stories.append(story_dict)

        # 3. Sort: ưu tiên stories của followed trước, sau đó mới theo createdAt giảm dần
        filtered_stories.sort(key=lambda s: (s["_isFollowed"], s.get("createdAt")), reverse=True)

        # Xóa trường _isFollowed trước khi trả về
        for s in filtered_stories:
            s.pop("_isFollowed", None)

        return filtered_stories
    
    @staticmethod
    async def delete(story_id: str) -> bool:
        result = await StoryRepository.collection.update_one(
            {"_id": ObjectId(story_id)},
            {"$set": {"status": "off"}}
        )
        return result.modified_count > 0
