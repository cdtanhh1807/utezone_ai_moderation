from core.database import db
from bson import ObjectId


class PolicyRepository:

    collection = db["policy"]

    @staticmethod
    async def find_all() -> list[dict]:
        policies = []
        async for policy in PolicyRepository.collection.find({"hidden": {"$exists": False}}).sort("createdAt", -1):
            policies.append(policy)
        return policies
    
    @staticmethod
    async def find_all_action() -> list[dict]:
        pipeline = [
            {
                "$match": {"action": {"$exists": True}}
            },
            {
                "$group": {
                    "_id": "$action"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "action": "$_id"
                }
            }
        ]
        actions = []
        async for doc in PolicyRepository.collection.aggregate(pipeline):
            actions.append(doc)
        return actions
    
    @staticmethod
    async def find_by_id(policy_id: str) -> dict | None:
        return await PolicyRepository.collection.find_one({"_id": ObjectId(policy_id)})

    @staticmethod
    async def update(data: dict) -> dict | None:
        policy_id = data.pop("id", None)
        if not policy_id: return None
        await PolicyRepository.collection.update_one(
            {"_id": ObjectId(policy_id)},
            {"$set": data}
        )
        return await PolicyRepository.find_by_id(policy_id)
    
    @staticmethod
    async def unset_action(data: dict) -> dict | None:
        policy_id = data.pop("id", None)
        if not policy_id: return None
        await PolicyRepository.collection.update_one(
            {"_id": ObjectId(policy_id)},
            {"$unset": {"action": ""}}
        )
        return await PolicyRepository.find_by_id(policy_id)
    
    @staticmethod
    async def insert(data: dict) -> dict:
        result = await PolicyRepository.collection.insert_one(data)
        new_policy = await PolicyRepository.collection.find_one({"_id": result.inserted_id})
        return new_policy
    
    @staticmethod
    async def get_all_with_content(content: str) -> list[dict]:
        policies = []
        query = {
            "hidden": {"$exists": False},
            "$or": [
                {"name": {"$regex": content, "$options": "i"}},
                {"description": {"$regex": content, "$options": "i"}}
            ]
        }
        
        async for policy in PolicyRepository.collection.find(query).sort("createdAt", -1):
            policies.append(policy)

        return policies

    


