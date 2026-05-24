from datetime import datetime, timedelta, timezone
from core.database import db
from bson import ObjectId


class ComplaintRepository:

    collection = db["complaint"]

    @staticmethod
    async def find_all() -> list[dict]:
        complaints = []
        async for complaint in ComplaintRepository.collection.find({"verify": {"$exists": False}}):
            complaints.append(complaint)
        return complaints
    
    @staticmethod
    async def find_by_id(complaint_id: str) -> dict | None:
        return await ComplaintRepository.collection.find_one({"_id": ObjectId(complaint_id)})
    
    @staticmethod
    async def update(data: dict) -> dict | None:
        complaint_id = data.pop("id", None)
        if not complaint_id: return None
        await ComplaintRepository.collection.update_one(
            {"_id": ObjectId(complaint_id)},
            {"$set": data}
        )
        return await ComplaintRepository.find_by_id(complaint_id)
    
    @staticmethod
    async def insert(data: dict) -> dict:
        result = await ComplaintRepository.collection.insert_one(data)
        new_c = await ComplaintRepository.collection.find_one({"_id": result.inserted_id})
        return new_c

    @staticmethod
    async def get_complaint_of_day() -> int:
        posts_today = await ComplaintRepository.collection.find({
            'verify': { "$exists": False }
        }).to_list(None) 
        return len(posts_today)