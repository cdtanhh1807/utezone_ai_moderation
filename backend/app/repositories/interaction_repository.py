from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Set

class InteractionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_interacted_emails(self, user_email: str) -> Set[str]:
        # 1. React
        react_pipeline = [
            {"$match": {
                "visibility": "public",
                "status": "active",
                "createdBy": {"$exists": True, "$ne": None}  # bảo vệ
            }},
            {"$project": {
                "allReact": {
                    "$concatArrays": [
                        "$react.love", "$react.like", "$react.haha",
                        "$react.wow", "$react.sad", "$react.angry"
                    ]
                },
                "createdBy": 1
            }},
            {"$unwind": "$allReact"},
            {"$match": {"allReact": user_email}},
            {"$project": {"_id": 0, "they": "$createdBy"}}
        ]
        reacted_to = {doc.get("they") async for doc in self.db.post.aggregate(react_pipeline)}
        reacted_to.discard(None)

        # 2. Comment
        comment_pipeline = [
            {"$match": {
                "visibility": "public",
                "status": "active",
                "createdBy": {"$exists": True, "$ne": None}
            }},
            {"$unwind": "$comments"},
            {"$match": {"comments.commentBy": user_email}},
            {"$project": {"_id": 0, "they": "$createdBy"}}
        ]
        commented_to = {doc.get("they") async for doc in self.db.post.aggregate(comment_pipeline)}
        commented_to.discard(None)

        # 3. Message (nếu có collection messages)
        sent_to       = set(await self.db.message.distinct("receiver", {"sender": user_email}))
        received_from = set(await self.db.message.distinct("sender",   {"receiver": user_email}))

        all_emails = reacted_to | commented_to | sent_to | received_from
        all_emails.discard(user_email)
        return all_emails