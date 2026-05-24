from core.database import db

class AnnounceRepository:

    collection = db["announce"]

    @staticmethod
    async def insert(data: dict) -> dict:
        result = await AnnounceRepository.collection.insert_one(data)
        new = await AnnounceRepository.collection.find_one({"_id": result.inserted_id})
        return new
    
    @staticmethod
    async def get_all_by_receiver_email(email: str) -> list[dict]:
        cursor = AnnounceRepository.collection.find({"receiverEmail": email})
        docs = await cursor.to_list(length=None)
        return docs
