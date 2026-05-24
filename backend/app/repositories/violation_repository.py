from datetime import datetime, timedelta
from pymongo import ReturnDocument
from core.database import db
from bson import ObjectId


class ViolationRepository:

    collection = db["violation"]

    @staticmethod
    async def find_by_violator_and_policy(violatorEmail: str, policyId: str) -> dict | None:
        return await ViolationRepository.collection.find_one({
            "violatorEmail": violatorEmail,
            "policyId": policyId
        })
    
    @staticmethod
    async def add_or_create_violation(violatorEmail: str, policyId: str, timestamp, blocker: str) -> dict | None:
        update_obj = {
        "blocker": blocker,
        "at": timestamp
        }

        doc = await ViolationRepository.collection.find_one_and_update(
            {"violatorEmail": violatorEmail, "policyId": policyId},
            {
                "$push": {"updatedAt": update_obj},
                "$setOnInsert": {
                    "violatorEmail": violatorEmail,
                    "policyId": policyId
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        return doc
    
    @staticmethod
    async def find_by_id(violation_id: str) -> dict | None:
        return await ViolationRepository.collection.find_one({"_id": ObjectId(violation_id)})

    @staticmethod
    async def find_and_remove_update_at(
        violatorEmail: str,
        policyId: str,
        approveAt: datetime
    ) -> dict | None:

        range_ms = timedelta(milliseconds=5)

        return await ViolationRepository.collection.find_one_and_update(
            {
                "violatorEmail": violatorEmail,
                "policyId": policyId,
                "updatedAt.at": {
                    "$gte": approveAt - range_ms,
                    "$lte": approveAt + range_ms
                }
            },
            {
                "$pull": {
                    "updatedAt": {
                        "at": {
                            "$gte": approveAt - range_ms,
                            "$lte": approveAt + range_ms
                        }
                    }
                }
            },
            return_document=ReturnDocument.AFTER
        )


