from core.database import db

class PostCatalogRepository:

    collection = db["post_catalog"]

    @staticmethod
    async def insert(data: dict) -> dict:
        result = await PostCatalogRepository.collection.insert_one(data)
        item = await PostCatalogRepository.collection.find_one({"_id": result.inserted_id})
        return item
    
    @staticmethod
    async def find_by_post_id(post_id: str) -> dict | None:
        return await PostCatalogRepository.collection.find_one({"post_id": post_id})

    @staticmethod
    async def update(data: dict) -> dict | None:
        post_id = data.pop("post_id", None)
        if not post_id: return None
        await PostCatalogRepository.collection.update_one(
            {"post_id": post_id},
            {"$set": data}
        )
        return await PostCatalogRepository.find_by_post_id(post_id)
    
    @staticmethod
    async def delete(post_id: str) -> bool:
        result = await PostCatalogRepository.collection.delete_one(
            {"post_id": post_id}
        )
        return result.deleted_count > 0
    
    @staticmethod
    async def find_by_email(email: str):
        cursor = PostCatalogRepository.collection.find(
            {"email": email}
        )
        documents = await cursor.to_list(length=None)
        return documents
    
    @staticmethod
    async def find_all():
        cursor = PostCatalogRepository.collection.find()
        documents = await cursor.to_list(length=None)
        return documents