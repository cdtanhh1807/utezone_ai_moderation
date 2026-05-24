from typing import Optional
from core.database import db
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from pymongo import ReturnDocument

class BanRepository:

    collection = db["ban"]

    @staticmethod
    async def find_all() -> list[dict]:
        bans = []
        async for ban in BanRepository.collection.find().sort("violations.beginAt", -1):
            bans.append(ban)
        return bans

    @staticmethod
    async def add_or_update_ban(violatorEmail: str, violationId: str) -> dict | None:
        now = datetime.now()
        end_at = now + timedelta(days=1)
        # end_at = now

        doc = await BanRepository.collection.find_one_and_update(
            {
                "violatorEmail": violatorEmail,
                "violations.violationId": violationId
            },
            {
                "$set": {
                    "violations.$.beginAt": now,
                    "violations.$.endAt": end_at
                }
            },
            return_document=ReturnDocument.AFTER
        )

        if doc:
            return doc

        doc = await BanRepository.collection.find_one({"violatorEmail": violatorEmail})

        if doc:
            updated_doc = await BanRepository.collection.find_one_and_update(
                {"violatorEmail": violatorEmail},
                {
                    "$push": {
                        "violations": {
                            "violationId": violationId,
                            "beginAt": now,
                            "endAt": end_at
                        }
                    }
                },
                return_document=ReturnDocument.AFTER
            )
            if updated_doc:
                return updated_doc
        else:
            new_doc = {
                "violatorEmail": violatorEmail,
                "violations": [
                    {
                        "violationId": violationId,
                        "beginAt": now,
                        "endAt": end_at
                    }
                ]
            }
            result = await BanRepository.collection.insert_one(new_doc)
            doc = await BanRepository.collection.find_one({"_id": result.inserted_id})
            return doc
        
        return None
    
    @staticmethod
    async def find_and_delete_ban(
        violatorEmail: str,
        violationId: str,
        approveAt: datetime
    ) -> Optional[dict]:
        approveAt = approveAt.replace(tzinfo=timezone.utc)
        start_time = approveAt - timedelta(minutes=1)
        end_time = approveAt + timedelta(minutes=1)

        # 1. Xóa phần tử trong mảng violations
        result = await BanRepository.collection.find_one_and_update(
            {
                "violatorEmail": violatorEmail,
                "violations": {
                    "$elemMatch": {
                        "violationId": violationId,
                        "beginAt": {
                            "$gte": start_time,
                            "$lte": end_time
                        }
                    }
                }
            },
            {
                "$pull": {
                    "violations": {
                        "violationId": violationId,
                        "beginAt": {
                            "$gte": start_time,
                            "$lte": end_time
                        }
                    }
                }
            },
            return_document=True  # trả về document **sau khi update**
        )

        if result:
            # 2. Nếu violations rỗng thì xóa cả document
            if not result.get("violations"):
                await BanRepository.collection.delete_one({"_id": result["_id"]})
            return result

        return None
    
    @staticmethod
    async def remove_expired_violations(email: str):
        now = datetime.now()

        await BanRepository.collection.update_one(
            { "violatorEmail": email },
            {
                "$pull": {
                    "violations": {
                        "endAt": { "$lte": now }
                    }
                }
            }
        )

        await BanRepository.collection.delete_one({
            "violatorEmail": email,
            "violations": { "$size": 0 }
        })
